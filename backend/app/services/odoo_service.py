import xmlrpc.client
from typing import Dict, Any, List, Optional
from app.core.config import settings

class OdooService:
    """Helper service to connect and interact with Odoo ERP instance via XML-RPC APIs."""

    @staticmethod
    def check_connection() -> Dict[str, Any]:
        """Ping Odoo server common endpoint to check connectivity."""
        try:
            url = f"{settings.ODOO_URL}/xmlrpc/2/common"
            common = xmlrpc.client.ServerProxy(url)
            version = common.version()
            return {
                "connected": True,
                "server_version": version.get("server_version", "Unknown"),
                "protocol_version": version.get("protocol_version", "Unknown"),
                "odoo_url": settings.ODOO_URL
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "odoo_url": settings.ODOO_URL
            }

    @staticmethod
    def authenticate() -> Dict[str, Any]:
        """Authenticate user against target Odoo Database."""
        try:
            url = f"{settings.ODOO_URL}/xmlrpc/2/common"
            common = xmlrpc.client.ServerProxy(url)
            uid = common.authenticate(
                settings.ODOO_DB,
                settings.ODOO_USER,
                settings.ODOO_PASSWORD,
                {}
            )
            if uid:
                return {"authenticated": True, "uid": uid}
            return {"authenticated": False, "error": "Invalid DB credentials or user unauthorized."}
        except Exception as e:
            return {"authenticated": False, "error": str(e)}

    @staticmethod
    def search_read_records(model_name: str, domain: Optional[list] = None, fields: Optional[list] = None, limit: int = 10) -> Dict[str, Any]:
        """Generic XML-RPC search_read executor for any Odoo model (res.partner, product.product, sale.order, etc.)."""
        auth_res = OdooService.authenticate()
        if not auth_res.get("authenticated"):
            return {
                "success": False,
                "error": auth_res.get("error", "Authentication failed"),
                "message": "Failed to connect/authenticate with Odoo. Check ODOO_URL, ODOO_DB, ODOO_USER, and ODOO_PASSWORD in .env"
            }
            
        uid = auth_res["uid"]
        domain = domain or []
        fields = fields or ["id", "name"]
        
        try:
            url = f"{settings.ODOO_URL}/xmlrpc/2/object"
            models = xmlrpc.client.ServerProxy(url)
            records = models.execute_kw(
                settings.ODOO_DB,
                uid,
                settings.ODOO_PASSWORD,
                model_name,
                "search_read",
                [domain],
                {"fields": fields, "limit": limit}
            )
            return {
                "success": True,
                "model": model_name,
                "count": len(records),
                "data": records
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
