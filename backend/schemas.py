from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentBase(BaseModel):
    service: str
    user_id: int
    attendant_id: int
    scheduled_time: datetime

    class Config:
        from_attributes = True

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class AppointmentUpdate(BaseModel):
    status: Optional[str] = None