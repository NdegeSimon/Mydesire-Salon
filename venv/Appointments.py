# routes/appointments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import users.db
from models import Appointment
from schemas import AppointmentCreate, AppointmentResponse

router = APIRouter(prefix="/book", tags=["Appointments"])


appointments_db = []

# -----------------------------
# Data Models
# -----------------------------
class Appointment(BaseModel):
    id: int
    service: str
    user_id: int
    attendant_id: int
    date: str
    time: str
    status: str = "pending"  # pending, confirmed, rejected, completed

# -----------------------------
# API Endpoints
# -----------------------------


@router.post("/", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    # Check if appointment time is already booked
    existing = db.query(Appointment).filter(
        Appointment.attendant_id == appointment.attendant_id,
        Appointment.scheduled_time == appointment.scheduled_time
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="This time slot is already booked.")

    new_appointment = Appointment(
        user_id=appointment.user_id,
        attendant_id=appointment.attendant_id,
        service_id=appointment.service_id,
        scheduled_time=appointment.scheduled_time,
        status="pending",  # default status
        created_at=datetime.utcnow()
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment

router = APIRouter(prefix="/appointments", tags=["appointments"])

# -----------------------------
# Mock Database
# -----------------------------

# Get specific appointment
@router.get("/{appointment_id}", response_model=Appointment)
def get_appointment(appointment_id: int):
    for appointment in appointments_db:
        if appointment.id == appointment_id:
            return appointment
    raise HTTPException(status_code=404, detail="Appointment not found")

# Get appointments by user_id
@router.get("/", response_model=List[Appointment])
def get_appointments(user_id: Optional[int] = None, attendant_id: Optional[int] = None):
    if user_id:
        return [appt for appt in appointments_db if appt.user_id == user_id]
    if attendant_id:
        return [appt for appt in appointments_db if appt.attendant_id == attendant_id]
    return appointments_db

# Approve appointment
@router.patch("/{appointment_id}/approve")
def approve_appointment(appointment_id: int):
    for appointment in appointments_db:
        if appointment.id == appointment_id:
            if appointment.status != "pending":
                raise HTTPException(status_code=400, detail="Only pending appointments can be approved")
            appointment.status = "confirmed"
            return {"message": "Appointment approved", "appointment": appointment}
    raise HTTPException(status_code=404, detail="Appointment not found")

# Reject appointment
@router.patch("/{appointment_id}/reject")
def reject_appointment(appointment_id: int):
    for appointment in appointments_db:
        if appointment.id == appointment_id:
            if appointment.status != "pending":
                raise HTTPException(status_code=400, detail="Only pending appointments can be rejected")
            appointment.status = "rejected"
            return {"message": "Appointment rejected", "appointment": appointment}
    raise HTTPException(status_code=404, detail="Appointment not found")

# Complete appointment
@router.patch("/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    for appointment in appointments_db:
        if appointment.id == appointment_id:
            if appointment.status != "confirmed":
                raise HTTPException(status_code=400, detail="Only confirmed appointments can be completed")
            appointment.status = "completed"
            return {"message": "Appointment completed", "appointment": appointment}
    raise HTTPException(status_code=404, detail="Appointment not found")

# Delete appointment (cancel by user)
@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int):
    for appointment in appointments_db:
        if appointment.id == appointment_id:
            if appointment.status != "pending":
                raise HTTPException(status_code=400, detail="Only pending appointments can be cancelled")
            appointments_db.remove(appointment)
            return {"message": "Appointment cancelled"}
    raise HTTPException(status_code=404, detail="Appointment not found")
