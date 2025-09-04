# routes/appointments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import Appointment, User, SalonAttendant
from schemas import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

def create_appointment(user_email, salon_attendant_id, service, appointment_time):
    """
    Create a new appointment for a user.
    
    Args:
        user_email (str): The email of the user making the appointment.
        salon_attendant_id (int): The ID of the salon attendant.
        service (str): The service to be provided.
        appointment_time (datetime): The scheduled time of the appointment.
    
    Returns:
        Appointment: The created appointment object, or None if failed.
    """
    user = session.query(User).filter_by(email=user_email).first()
    if not user:
        print("User not found!")
        return None
    
    if not session.query(SalonAttendant).filter_by(id=salon_attendant_id).first():
        print("Salon attendant not found!")
        return None
    
    new_appointment = Appointment(
        user_id=user.id,
        salon_attendant_id=salon_attendant_id,
        service=service,
        appointment_time=appointment_time,
        status="pending"
    )
    session.add(new_appointment)
    session.commit()
    print(f"Appointment created for {user.name} at {appointment_time}")
    send_notification(user, new_appointment, method="email")  # Auto-notify on creation
    return new_appointment

def send_notification(user, appointment, method="email"):
    """
    Send a notification (email or SMS) about an appointment.
    
    Args:
        user (User): The user object.
        appointment (Appointment): The appointment object.
        method (str): "email" or "sms" (default: "email").
    
    Returns:
        bool: True if successful, False otherwise.
    """
    message = f"Dear {user.name},\nYour appointment for {appointment.service} at {appointment.appointment_time} is {appointment.status}.\nThank you, My Desire Salon!"
    
    if method == "email":
        msg = MIMEText(message)
        msg["Subject"] = "Appointment Confirmation"
        msg["From"] = "your_email@example.com"  # Replace with EMAIL_USER
        msg["To"] = user.email

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login("your_email@example.com", "your_email_password")  # Replace with credentials
                server.sendmail("your_email@example.com", user.email, msg.as_string())
            print(f"Email sent to {user.email}")
            return True
        except Exception as e:
            print(f"Email failed: {e}")
            return False
    
    elif method == "sms":
        client = Client("your_twilio_sid", "your_twilio_auth_token")  # Replace with credentials
        try:
            message = client.messages.create(
                body=message,
                from_="your_twilio_number",  # Replace with TWILIO_PHONE_NUMBER
                to=user.phone  # Use user.phone from User model
            )
            print(f"SMS sent, SID: {message.sid}")
            return True
        except TwilioRestException as e:
            print(f"SMS failed: {e}")
            return False
    
    return False

def update_appointment_status(appointment_id, new_status):
    """
    Update the status of an appointment and send a notification.
    
    Args:
        appointment_id (int): The ID of the appointment.
        new_status (str): The new status (e.g., "confirmed", "completed", "canceled").
    
    Returns:
        bool: True if successful, False otherwise.
    """
    appointment = session.query(Appointment).filter_by(id=appointment_id).first()
    if not appointment:
        print("Appointment not found!")
        return False
    
    appointment.status = new_status
    session.commit()
    print(f"Appointment {appointment_id} status updated to {new_status}")
    
    user = session.query(User).filter_by(id=appointment.user_id).first()
    if user:
        send_notification(user, appointment, method="email")
    return True

def get_user_appointments(user_email):
    """
    Retrieve all appointments for a user.
    
    Args:
        user_email (str): The email of the user.
    
    Returns:
        list: List of Appointment objects.
    """
    user = session.query(User).filter_by(email=user_email).first()
    if not user:
        print("User not found!")
        return []
    
    return user.appointments

# Create the database tables
Base.metadata.create_all(engine)
