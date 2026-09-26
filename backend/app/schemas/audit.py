from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AuditLogCreate(BaseModel):
    user_id: Optional[str] = "System"
    action: str
    entity: str
    entity_id: Optional[str] = None
    ip_address: Optional[str] = None

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[str] = None
    action: str
    entity: str
    entity_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    ip_address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
