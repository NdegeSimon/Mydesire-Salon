# routes/appointments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import Appointment
from schemas import AppointmentCreate, AppointmentResponse, AppointmentUpdate

router = APIRouter(prefix="/appointments", tags=["appointments"])

# Create appointment
@router.post("/", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    # Check if appointment time is already booked
    existing = db.query(Appointment).filter(
        Appointment.salon_attendant_id == appointment.attendant_id,
        Appointment.appointment_time == appointment.scheduled_time
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="This time slot is already booked.")

    new_appointment = Appointment(
        user_id=appointment.user_id,
        salon_attendant_id=appointment.attendant_id,
        service=appointment.service,
        appointment_time=appointment.scheduled_time,
        status="pending"
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment

# Get specific appointment
@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

# Get appointments by user_id or attendant_id
@router.get("/", response_model=list[AppointmentResponse])
def get_appointments(user_id: int = None, attendant_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Appointment)
    
    if user_id:
        query = query.filter(Appointment.user_id == user_id)
    if attendant_id:
        query = query.filter(Appointment.salon_attendant_id == attendant_id)
        
    return query.all()

# Update appointment status
@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: int, appointment_update: AppointmentUpdate, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment_update.status:
        if appointment.status == "pending" and appointment_update.status in ["confirmed", "rejected"]:
            appointment.status = appointment_update.status
        elif appointment.status == "confirmed" and appointment_update.status == "completed":
            appointment.status = appointment_update.status
        else:
            raise HTTPException(status_code=400, detail="Invalid status transition")
    
    db.commit()
    db.refresh(appointment)
    return appointment

# Delete appointment (cancel by user)
@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending appointments can be cancelled")
    
    db.delete(appointment)
    db.commit()
    return {"message": "Appointment cancelled"}
