from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.db.database import get_db, dict_cursor
from app.api.deps import get_current_user
from app.schemas.dashboard import SearchResponse

router = APIRouter(prefix="/products", tags=["Product Search"])


@router.get("/search", response_model=SearchResponse)
def search_products(
    q: str = Query(..., min_length=1, description="Search term — matched against product name and SKU"),
    category_id: Optional[str] = Query(None, description="Narrow results to a specific category UUID"),
    active_only: bool = Query(True, description="Only return active products"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    SKU / Product name search for the global search bar and filter auto-complete.

    Performs a case-insensitive prefix/substring match on **both** `name` and `sku`
    so warehouse staff can find items by either field quickly.

    Query params:
    - **q**: required search string (min 1 char)
    - **category_id**: optional UUID to restrict to one category
    - **active_only**: default True — exclude soft-deleted products
    - **skip / limit**: standard pagination (default 20 results)
    """
    term = f"%{q}%"
    conditions = ["(p.name ILIKE %s OR p.sku ILIKE %s)"]
    params: list = [term, term]

    if active_only:
        conditions.append("p.is_active = TRUE")

    if category_id and category_id.strip().lower() not in ("", "null", "string"):
        conditions.append("p.category_id = %s")
        params.append(category_id)

    where_clause = " AND ".join(conditions)

    with dict_cursor(conn) as cur:
        cur.execute(
            f"""
            SELECT
                p.id,
                p.name,
                p.sku,
                p.unit_of_measure,
                p.category_id,
                p.is_active
            FROM products p
            WHERE {where_clause}
            ORDER BY
                -- Exact SKU match first, then prefix matches, then substring
                CASE
                    WHEN p.sku ILIKE %s THEN 0
                    WHEN p.name ILIKE %s THEN 1
                    ELSE 2
                END,
                p.name
            LIMIT %s OFFSET %s
            """,
            params + [q, f"{q}%", limit, skip],
        )
        rows = [dict(r) for r in cur.fetchall()]

        cur.execute(
            f"SELECT COUNT(*) AS cnt FROM products p WHERE {where_clause}",
            params,
        )
        total = (cur.fetchone() or {}).get("cnt", 0) or 0

    return {"items": rows, "total": int(total), "query": q}
