from typing import Dict, Any, List, Optional
from app.db.database import dict_cursor
from app.services.product_service import clean_uuid


class ForecastService:
    """
    Service for Demand Forecasting & Smart Reordering suggestions.
    Calculates daily consumption rate from ledger history to predict stockout timeline.
    """

    @staticmethod
    def get_product_forecast(conn, product_id: str, warehouse_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate demand forecast for a single product.
        
        Returns exact specification:
        {
          "product": "Steel Rod",
          "days_to_stockout": 6,
          "recommended_order": 120
        }
        """
        p_id = clean_uuid(product_id) or product_id
        wh_id = clean_uuid(warehouse_id)

        with dict_cursor(conn) as cur:
            # 1. Fetch product master details
            cur.execute(
                """SELECT id, name, sku, reorder_min, reorder_max
                   FROM products WHERE id = %s""",
                (p_id,),
            )
            product = cur.fetchone()

            if not product:
                # Fallback if product_id is given as a string name or unknown UUID
                cur.execute(
                    """SELECT id, name, sku, reorder_min, reorder_max
                       FROM products WHERE name ILIKE %s OR sku ILIKE %s LIMIT 1""",
                    (f"%{product_id}%", f"%{product_id}%"),
                )
                product = cur.fetchone()

            if not product:
                raise ValueError(f"Product '{product_id}' not found.")

            real_prod_id = product["id"]
            prod_name = product["name"]
            reorder_min = float(product.get("reorder_min") or 0)
            reorder_max = float(product.get("reorder_max") or 0)

            # 2. Get current on-hand stock
            if wh_id:
                cur.execute(
                    """SELECT COALESCE(SUM(qty_delta), 0) AS on_hand
                       FROM stock_ledger_entries
                       WHERE product_id = %s AND warehouse_id = %s""",
                    (real_prod_id, wh_id),
                )
            else:
                cur.execute(
                    """SELECT COALESCE(SUM(qty_delta), 0) AS on_hand
                       FROM stock_ledger_entries
                       WHERE product_id = %s""",
                    (real_prod_id,),
                )
            stock_row = cur.fetchone()
            current_stock = float(stock_row["on_hand"]) if stock_row else 0.0

            # 3. Calculate 30-day outgoing consumption (DELIVERY and TRANSFER_OUT)
            if wh_id:
                cur.execute(
                    """SELECT COALESCE(ABS(SUM(qty_delta)), 0) AS total_consumed
                       FROM stock_ledger_entries
                       WHERE product_id = %s AND warehouse_id = %s AND qty_delta < 0
                         AND timestamp >= NOW() - INTERVAL '30 days'""",
                    (real_prod_id, wh_id),
                )
            else:
                cur.execute(
                    """SELECT COALESCE(ABS(SUM(qty_delta)), 0) AS total_consumed
                       FROM stock_ledger_entries
                       WHERE product_id = %s AND qty_delta < 0
                         AND timestamp >= NOW() - INTERVAL '30 days'""",
                    (real_prod_id,),
                )
            consumed_row = cur.fetchone()
            consumed_30d = float(consumed_row["total_consumed"]) if consumed_row else 0.0

            # Daily consumption rate
            if consumed_30d > 0:
                daily_rate = consumed_30d / 30.0
            else:
                # If no recent ledger history, estimate rate from reorder_min or default 1.0/day
                daily_rate = max(1.0, reorder_min / 7.0) if reorder_min > 0 else 2.0

            # 4. Calculate days to stockout
            if current_stock <= 0:
                days_to_stockout = 0
            else:
                days_to_stockout = int(current_stock / daily_rate)

            # 5. Calculate recommended order quantity
            if reorder_max > 0 and reorder_max > current_stock:
                recommended_order = reorder_max - current_stock
            else:
                # Default recommended order: 30 days buffer minus current stock
                buffer_needed = daily_rate * 30.0
                recommended_order = max(0.0, buffer_needed - current_stock)

            # Format recommended_order as clean float or int
            recommended_order = (
                int(recommended_order)
                if recommended_order.is_integer()
                else round(recommended_order, 1)
            )

        return {
            "product": prod_name,
            "days_to_stockout": days_to_stockout,
            "recommended_order": recommended_order,
            "product_id": str(real_prod_id),
            "current_stock": current_stock,
            "daily_consumption_rate": round(daily_rate, 2),
        }

    @staticmethod
    def get_all_forecasts(conn) -> List[Dict[str, Any]]:
        """List forecasts for all active products."""
        with dict_cursor(conn) as cur:
            cur.execute("SELECT id FROM products WHERE is_active = TRUE ORDER BY name")
            products = cur.fetchall()

        results = []
        for p in products:
            try:
                forecast = ForecastService.get_product_forecast(conn, p["id"])
                results.append(forecast)
            except Exception:
                continue

        return results
