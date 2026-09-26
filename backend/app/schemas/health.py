from typing import Dict, Any, Optional
from pydantic import BaseModel

class HealthCheck(BaseModel):
    status: str
    app_name: str
    version: str
    database: str
    timestamp: str
