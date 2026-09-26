import os
import re
import logging
from typing import Dict, Any, List, Optional
from app.db.database import dict_cursor
from app.core.config import settings

logger = logging.getLogger(__name__)

# Attempt to import google-genai
try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class AIService:
    """
    AI Assistant Service for natural-language warehouse & stock queries.
    Integrates Gemini API when configured, with a smart fallback DB query engine.
    """

    @staticmethod
    def get_inventory_context(conn) -> Dict[str, Any]:
        """Fetch current stock snapshot and metadata from the database."""
        with dict_cursor(conn) as cur:
            # 1. On-hand stock per product per warehouse
            cur.execute(
                """
                SELECT
                    p.id           AS product_id,
                    p.name         AS product_name,
                    p.sku          AS sku,
                    p.unit_of_measure,
                    p.reorder_min,
                    COALESCE(w.name, 'Main Warehouse') AS warehouse_name,
                    COALESCE(w.code, 'WH01')           AS warehouse_code,
                    COALESCE(SUM(sle.qty_delta), 0)    AS quantity
                FROM products p
                LEFT JOIN stock_ledger_entries sle ON sle.product_id = p.id
                LEFT JOIN warehouses w ON w.id = sle.warehouse_id
                WHERE p.is_active = TRUE
                GROUP BY p.id, p.name, p.sku, p.unit_of_measure, p.reorder_min, w.id, w.name, w.code
                """
            )
            stock_rows = [dict(r) for r in cur.fetchall()]

            # 2. Total active products count
            cur.execute("SELECT COUNT(*) AS cnt FROM products WHERE is_active = TRUE")
            total_products = (cur.fetchone() or {}).get("cnt", 0)

            # 3. Pending document counts
            cur.execute("SELECT COUNT(*) AS cnt FROM receipts WHERE status NOT IN ('Done', 'Cancelled', 'Canceled')")
            pending_receipts = (cur.fetchone() or {}).get("cnt", 0)

            cur.execute("SELECT COUNT(*) AS cnt FROM deliveries WHERE status NOT IN ('Done', 'Cancelled', 'Canceled')")
            pending_deliveries = (cur.fetchone() or {}).get("cnt", 0)

            cur.execute("SELECT COUNT(*) AS cnt FROM transfers WHERE status NOT IN ('Done', 'Cancelled', 'Canceled')")
            pending_transfers = (cur.fetchone() or {}).get("cnt", 0)

        # Categorize low stock items
        low_stock_list = []
        for r in stock_rows:
            qty = float(r["quantity"])
            reorder_min = float(r.get("reorder_min") or 0)
            if (qty <= reorder_min and reorder_min > 0) or qty <= 0:
                low_stock_list.append(r)

        return {
            "stock_levels": stock_rows,
            "total_products": total_products,
            "pending_receipts": pending_receipts,
            "pending_deliveries": pending_deliveries,
            "pending_transfers": pending_transfers,
            "low_stock_items": low_stock_list,
        }

    @staticmethod
    def process_query(conn, query: str) -> Dict[str, Any]:
        """
        Process a user natural language query and return an AI answer.
        """
        context = AIService.get_inventory_context(conn)
        api_key = (
            getattr(settings, "GEMINI_API_KEY", None)
            or getattr(settings, "GOOGLE_API_KEY", None)
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )

        # Clean API key if placeholder string
        if api_key and api_key.strip().lower() in ("your_api_key_here", "none", "null", ""):
            api_key = None

        # Try Gemini API if key is available
        if HAS_GENAI and api_key:
            for model_name in ("gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"):
                try:
                    client = genai.Client(api_key=api_key.strip())
                    prompt = (
                        "You are StockSense AI, an intelligent warehouse management assistant.\n"
                        "Use the following real-time inventory database context to answer the user's question accurately, concisely, and directly.\n\n"
                        f"INVENTORY CONTEXT:\n{context}\n\n"
                        f"USER QUESTION: {query}\n\n"
                        "ANSWER:"
                    )
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        return {
                            "answer": response.text.strip(),
                            "context": {"source": model_name},
                        }
                except Exception as e:
                    print(f"[AI SERVICE WARNING] Gemini model {model_name} error: {e}")
                    logger.warning(f"Gemini API model {model_name} failed ({e}). Trying next model.")
        else:
            print(f"[AI SERVICE NOTICE] Gemini API Key present: {bool(api_key)}, SDK Available: {HAS_GENAI}")

        # Local Smart Query Solver Fallback
        answer = AIService._smart_query_fallback(query, context)
        return {
            "answer": answer,
            "context": {"source": "local_smart_engine"},
        }

    @staticmethod
    def _smart_query_fallback(query: str, context: Dict[str, Any]) -> str:
        """
        Smart NLP pattern match and SQL context solver when AI API is offline/unconfigured.
        """
        q_lower = query.lower().strip()
        stock_rows = context["stock_levels"]

        # 1. Search for specific product and/or warehouse/rack in query
        # Example query: "How much steel is in Rack B?" or "how much Steel Rod is in Main Warehouse?"
        matched_items = []
        for r in stock_rows:
            p_name = r["product_name"].lower()
            p_sku = r["sku"].lower()
            wh_name = r["warehouse_name"].lower()
            wh_code = r["warehouse_code"].lower()

            # Check if query mentions product (name/sku/words) and/or warehouse (name/code/words)
            words = [w for w in p_name.split() if len(w) > 2]
            p_match = p_name in q_lower or p_sku in q_lower or any(w in q_lower for w in words)

            wh_words = [w for w in wh_name.split() if len(w) > 2]
            wh_match = wh_name in q_lower or wh_code in q_lower or any(w in q_lower for w in wh_words)

            if p_match or wh_match:
                matched_items.append((p_match, wh_match, r))

        # If both product and warehouse matched specifically
        exact_matches = [r for (pm, wm, r) in matched_items if pm and wm]
        if exact_matches:
            lines = []
            for r in exact_matches:
                qty_val = int(r['quantity']) if float(r['quantity']).is_integer() else r['quantity']
                lines.append(f"{r['warehouse_name']} currently contains {qty_val} {r['product_name']} ({r['unit_of_measure']}).")
            return " ".join(lines)

        # If location/rack matched specifically
        wh_only_matches = [r for (pm, wm, r) in matched_items if wm]
        if wh_only_matches:
            wh_target = wh_only_matches[0]["warehouse_name"]
            item_strs = []
            for r in wh_only_matches:
                qty_val = int(r['quantity']) if float(r['quantity']).is_integer() else r['quantity']
                item_strs.append(f"{qty_val} {r['product_name']}")
            return f"{wh_target} currently contains {', '.join(item_strs)}."

        # If product matched specifically
        prod_only_matches = [r for (pm, wm, r) in matched_items if pm]
        if prod_only_matches:
            lines = []
            for r in prod_only_matches:
                qty_val = int(r['quantity']) if float(r['quantity']).is_integer() else r['quantity']
                lines.append(f"{r['warehouse_name']} has {qty_val} {r['product_name']}.")
            return " ".join(lines)

        # 2. Low stock / Stockout queries
        if any(term in q_lower for term in ("low", "alert", "reorder", "out of stock", "shortage")):
            low_items = context["low_stock_items"]
            if not low_items:
                return "All product stock levels are healthy! No low stock alerts at this time."
            lines = [f"There are {len(low_items)} low stock alert(s):"]
            for r in low_items:
                lines.append(f"• {r['product_name']} ({r['sku']}): {r['quantity']} on hand (min threshold: {r['reorder_min']})")
            return "\n".join(lines)

        # 3. Pending work queries
        if any(term in q_lower for term in ("pending", "waiting", "open", "status")):
            return (
                f"Operational Work Status:\n"
                f"• Pending Receipts: {context['pending_receipts']}\n"
                f"• Pending Deliveries: {context['pending_deliveries']}\n"
                f"• Pending Internal Transfers: {context['pending_transfers']}"
            )

        # 4. Total stock / summary queries
        if any(term in q_lower for term in ("total", "summary", "how many", "all")):
            total_units = sum(float(r["quantity"]) for r in stock_rows)
            return f"StockSense currently tracks {context['total_products']} active products with a total of {total_units:,.0f} units on-hand."

        # Generic default response if query is ambiguous
        if stock_rows:
            sample = stock_rows[0]
            qty_val = int(sample['quantity']) if float(sample['quantity']).is_integer() else sample['quantity']
            return f"{sample['warehouse_name']} currently contains {qty_val} {sample['product_name']}."

        return "StockSense IMS is online. Currently no inventory entries found in database."
