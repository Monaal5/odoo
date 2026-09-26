import uuid
from typing import Optional
from app.db.database import dict_cursor


def clean_uuid(val: Optional[str]) -> Optional[str]:
    """Return valid UUID string or None if empty/placeholder/invalid."""
    if not val or str(val).strip().lower() in ("string", "null", "none", ""):
        return None
    try:
        return str(uuid.UUID(str(val)))
    except (ValueError, AttributeError):
        return None


class ProductService:

    # ─── Categories ──────────────────────────────────────────

    @staticmethod
    def create_category(conn, name: str, description: Optional[str]) -> dict:
        cat_id = str(uuid.uuid4())
        with dict_cursor(conn) as cur:
            cur.execute("SELECT id FROM categories WHERE name = %s", (name,))
            if cur.fetchone():
                raise ValueError(f"Category '{name}' already exists")
            cur.execute(
                """INSERT INTO categories (id, name, description)
                   VALUES (%s, %s, %s)
                   RETURNING id, name, description, created_at, updated_at""",
                (cat_id, name, description),
            )
            return dict(cur.fetchone())

    @staticmethod
    def list_categories(conn) -> list:
        with dict_cursor(conn) as cur:
            cur.execute(
                "SELECT id, name, description, created_at, updated_at FROM categories ORDER BY name"
            )
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def get_category(conn, category_id: str) -> Optional[dict]:
        with dict_cursor(conn) as cur:
            cur.execute(
                "SELECT id, name, description, created_at, updated_at FROM categories WHERE id = %s",
                (category_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def update_category(conn, category_id: str, name: Optional[str], description: Optional[str]) -> Optional[dict]:
        fields, values = [], []
        if name is not None:
            fields.append("name = %s"); values.append(name)
        if description is not None:
            fields.append("description = %s"); values.append(description)
        if not fields:
            return ProductService.get_category(conn, category_id)

        fields.append("updated_at = NOW()")
        values.append(category_id)
        sql = f"UPDATE categories SET {', '.join(fields)} WHERE id = %s RETURNING id, name, description, created_at, updated_at"
        with dict_cursor(conn) as cur:
            cur.execute(sql, values)
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def delete_category(conn, category_id: str) -> bool:
        with dict_cursor(conn) as cur:
            cur.execute("DELETE FROM categories WHERE id = %s RETURNING id", (category_id,))
            return cur.fetchone() is not None

    # ─── Products ────────────────────────────────────────────

    @staticmethod
    def create_product(conn, data: dict) -> dict:
        prod_id = clean_uuid(data.get("id")) or str(uuid.uuid4())
        category_id = clean_uuid(data.get("category_id"))
        with dict_cursor(conn) as cur:
            cur.execute("SELECT id FROM products WHERE sku = %s", (data["sku"],))
            if cur.fetchone():
                raise ValueError(f"SKU '{data['sku']}' already exists")
            cur.execute(
                """INSERT INTO products
                       (id, name, sku, category_id, unit_of_measure, reorder_min, reorder_max, description)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id, name, sku, category_id, unit_of_measure,
                             reorder_min, reorder_max, description, is_active,
                             created_at, updated_at""",
                (
                    prod_id, data["name"], data["sku"], category_id,
                    data.get("unit_of_measure", "units"),
                    data.get("reorder_min", 0), data.get("reorder_max", 0),
                    data.get("description"),
                ),
            )
            return dict(cur.fetchone())

    @staticmethod
    def list_products(conn, skip: int = 0, limit: int = 100,
                      category_id: Optional[str] = None,
                      search: Optional[str] = None) -> list:
        category_id = clean_uuid(category_id)
        sql = """
            SELECT id, name, sku, category_id, unit_of_measure,
                   reorder_min, reorder_max, description, is_active,
                   created_at, updated_at
            FROM products
            WHERE 1=1
        """
        params = []
        if category_id:
            sql += " AND category_id = %s"
            params.append(category_id)
        if search:
            sql += " AND (name ILIKE %s OR sku ILIKE %s)"
            params += [f"%{search}%", f"%{search}%"]
        sql += " ORDER BY name LIMIT %s OFFSET %s"
        params += [limit, skip]

        with dict_cursor(conn) as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def get_product(conn, product_id: str) -> Optional[dict]:
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT id, name, sku, category_id, unit_of_measure,
                          reorder_min, reorder_max, description, is_active,
                          created_at, updated_at
                   FROM products WHERE id = %s""",
                (product_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def update_product(conn, product_id: str, data: dict) -> Optional[dict]:
        allowed = ["name", "sku", "category_id", "unit_of_measure",
                   "reorder_min", "reorder_max", "description", "is_active"]
        fields, values = [], []
        for key in allowed:
            if key in data and data[key] is not None:
                val = data[key]
                if key == "category_id":
                    val = clean_uuid(val)
                fields.append(f"{key} = %s")
                values.append(val)
        if not fields:
            return ProductService.get_product(conn, product_id)

        fields.append("updated_at = NOW()")
        values.append(product_id)
        sql = f"UPDATE products SET {', '.join(fields)} WHERE id = %s RETURNING id, name, sku, category_id, unit_of_measure, reorder_min, reorder_max, description, is_active, created_at, updated_at"
        with dict_cursor(conn) as cur:
            cur.execute(sql, values)
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def delete_product(conn, product_id: str) -> bool:
        with dict_cursor(conn) as cur:
            cur.execute(
                "UPDATE products SET is_active = FALSE, updated_at = NOW() WHERE id = %s RETURNING id",
                (product_id,),
            )
            return cur.fetchone() is not None

    # ─── Warehouses ──────────────────────────────────────────

    @staticmethod
    def create_warehouse(conn, data: dict) -> dict:
        wh_id = clean_uuid(data.get("id")) or str(uuid.uuid4())
        parent_id = clean_uuid(data.get("parent_id"))
        with dict_cursor(conn) as cur:
            cur.execute("SELECT id FROM warehouses WHERE code = %s", (data["code"],))
            if cur.fetchone():
                raise ValueError(f"Warehouse code '{data['code']}' already exists")
            cur.execute(
                """INSERT INTO warehouses (id, name, code, address, parent_id)
                   VALUES (%s, %s, %s, %s, %s)
                   RETURNING id, name, code, address, parent_id, is_active, created_at, updated_at""",
                (wh_id, data["name"], data["code"], data.get("address"), parent_id),
            )
            return dict(cur.fetchone())

    @staticmethod
    def list_warehouses(conn, active_only: bool = False) -> list:
        sql = "SELECT id, name, code, address, parent_id, is_active, created_at, updated_at FROM warehouses"
        if active_only:
            sql += " WHERE is_active = TRUE"
        sql += " ORDER BY name"
        with dict_cursor(conn) as cur:
            cur.execute(sql)
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def get_warehouse(conn, warehouse_id: str) -> Optional[dict]:
        with dict_cursor(conn) as cur:
            cur.execute(
                "SELECT id, name, code, address, parent_id, is_active, created_at, updated_at FROM warehouses WHERE id = %s",
                (warehouse_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def update_warehouse(conn, warehouse_id: str, data: dict) -> Optional[dict]:
        allowed = ["name", "code", "address", "parent_id", "is_active"]
        fields, values = [], []
        for key in allowed:
            if key in data and data[key] is not None:
                val = data[key]
                if key == "parent_id":
                    val = clean_uuid(val)
                fields.append(f"{key} = %s")
                values.append(val)
        if not fields:
            return ProductService.get_warehouse(conn, warehouse_id)

        fields.append("updated_at = NOW()")
        values.append(warehouse_id)
        sql = f"UPDATE warehouses SET {', '.join(fields)} WHERE id = %s RETURNING id, name, code, address, parent_id, is_active, created_at, updated_at"
        with dict_cursor(conn) as cur:
            cur.execute(sql, values)
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def delete_warehouse(conn, warehouse_id: str) -> bool:
        with dict_cursor(conn) as cur:
            cur.execute(
                "UPDATE warehouses SET is_active = FALSE, updated_at = NOW() WHERE id = %s RETURNING id",
                (warehouse_id,),
            )
            return cur.fetchone() is not None
