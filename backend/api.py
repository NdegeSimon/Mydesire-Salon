from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uvicorn

from backend.database import SessionLocal, init_db
from backend.models import User, SalonAttendant, Appointment
from backend.schemas import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from backend.routes import signup, login
from backend.services.services import create_booking, send_notification, send_admin_notification

# Initialize the database
init_db()

app = FastAPI(title="My Desire Salon API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to My Desire Salon API"}

# Get all appointments
@app.get("/appointments/", response_model=List[AppointmentResponse])
def get_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    appointments = db.query(Appointment).offset(skip).limit(limit).all()
    # Map model fields to schema fields
    result = []
    for appointment in appointments:
        result.append({
            "id": appointment.id,
            "service": appointment.service,
            "user_id": appointment.user_id,
            "attendant_id": appointment.salon_attendant_id,
            "scheduled_time": appointment.appointment_time,
            "status": appointment.status,
            "created_at": appointment.created_at
        })
    return result

# Get appointment by ID
@app.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    # Map model fields to schema fields
    return {
        "id": appointment.id,
        "service": appointment.service,
        "user_id": appointment.user_id,
        "attendant_id": appointment.salon_attendant_id,
        "scheduled_time": appointment.appointment_time,
        "status": appointment.status,
        "created_at": appointment.created_at
    }

# Create appointment
@app.post("/appointments/", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.id == appointment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if attendant exists
    attendant = db.query(SalonAttendant).filter(SalonAttendant.id == appointment.attendant_id).first()
    if not attendant:
        raise HTTPException(status_code=404, detail="Attendant not found")
    
    # Create appointment
    db_appointment = Appointment(
        user_id=appointment.user_id,
        salon_attendant_id=appointment.attendant_id,
        service=appointment.service,
        appointment_time=appointment.scheduled_time,
        status="pending"
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    # Send notification to user
    message = f"Your booking for {appointment.service} is confirmed for {appointment.scheduled_time}."
    send_notification(db, appointment.user_id, message)
    
    # Send notification to admin
    admin_email = "harrisonodongo@gmail.com"
    send_admin_notification("New appointment booked", db_appointment, db)
    
    # Map model fields to schema fields
    return {
        "id": db_appointment.id,
        "service": db_appointment.service,
        "user_id": db_appointment.user_id,
        "attendant_id": db_appointment.salon_attendant_id,
        "scheduled_time": db_appointment.appointment_time,
        "status": db_appointment.status,
        "created_at": db_appointment.created_at
    }

# Update appointment
@app.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: int, appointment: AppointmentUpdate, db: Session = Depends(get_db)):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.status is not None:
        db_appointment.status = appointment.status
    
    db.commit()
    db.refresh(db_appointment)
    
    # Map model fields to schema fields
    return {
        "id": db_appointment.id,
        "service": db_appointment.service,
        "user_id": db_appointment.user_id,
        "attendant_id": db_appointment.salon_attendant_id,
        "scheduled_time": db_appointment.appointment_time,
        "status": db_appointment.status,
        "created_at": db_appointment.created_at
    }

# Delete appointment
@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db.delete(db_appointment)
    db.commit()
    return {"message": "Appointment deleted successfully"}

# User signup endpoint
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    phone: str
    password: str
@app.post("/signup")
def signup_user(user: UserCreate, db: Session = Depends(get_db)):
    result = signup(db, user.name, user.email, user.phone, user.password)
    return result


# User login endpoint
class UserLogin(BaseModel):
    identifier: str
    password: str

@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    result = login(db, user.identifier, user.password)
    return result

# Get all attendants
@app.get("/attendants/")
def get_attendants(db: Session = Depends(get_db)):
    attendants = db.query(SalonAttendant).all()
    return attendants

# Get user by ID
@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "created_at": user.created_at
    }

# Update user
@app.put("/users/{user_id}")
def update_user(user_id: int, name: str = None, email: str = None, phone: str = None, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if name:
        user.name = name
    if email:
        user.email = email
    if phone:
        user.phone = phone
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "created_at": user.created_at
    }

# Create attendant
@app.post("/attendants/")
def create_attendant(name: str, email: str, db: Session = Depends(get_db)):
    attendant = SalonAttendant(name=name, email=email)
    db.add(attendant)
    db.commit()
    db.refresh(attendant)
    return attendant

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)