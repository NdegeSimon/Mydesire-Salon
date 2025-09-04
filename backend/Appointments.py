from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from models import Appointment, User, SalonAttendant, session  # Import models and session

def create_appointment(user_email, salon_attendant_id, service, appointment_time, contact_method=None):
    """
    Create a new appointment for a user.
    
    Args:
        user_email (str): The email of the user making the appointment.
        salon_attendant_id (int): The ID of the salon attendant.
        service (str): The service to be provided.
        appointment_time (datetime): The scheduled time of the appointment.
        contact_method (str, optional): The user's preferred contact method (phone, sms, email, whatsapp). Defaults to None.
    
    Returns:
        Appointment: The created appointment object, or a string message if failed.
    """
    user = session.query(User).filter_by(email=user_email).first()
    if not user:
        return "Please log in to make an appointment."
    
    if not session.query(SalonAttendant).filter_by(id=salon_attendant_id).first():
        return "Salon attendant not found."
    
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
    send_notification(user, new_appointment, method=contact_method or "email")
    return new_appointment

def send_notification(user, appointment, method="email"):
    """
    Send a notification (phone call, SMS, email, or WhatsApp) about an appointment.
    
    Args:
        user (User): The user object.
        appointment (Appointment): The appointment object.
        method (str): The preferred contact method (phone, sms, email, whatsapp). Defaults to "email".
    
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
                to=user.phone
            )
            print(f"SMS sent, SID: {message.sid}")
            return True
        except TwilioRestException as e:
            print(f"SMS failed: {e}")
            return False
    
    elif method == "phone":
        # Placeholder for phone call (requires a telephony service like Twilio Voice)
        print(f"Phone call to {user.phone} would be initiated for {appointment.service}")
        return False  # Implement Twilio Voice or similar service
    
    elif method == "whatsapp":
        # Placeholder for WhatsApp (requires Twilio WhatsApp integration)
        client = Client("your_twilio_sid", "your_twilio_auth_token")  # Replace with credentials
        try:
            message = client.messages.create(
                body=message,
                from_="whatsapp:your_twilio_whatsapp_number",  # Replace with Twilio WhatsApp number
                to=f"whatsapp:{user.phone}"
            )
            print(f"WhatsApp sent, SID: {message.sid}")
            return True
        except TwilioRestException as e:
            print(f"WhatsApp failed: {e}")
            return False
    
    print(f"Unsupported contact method: {method}")
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
        send_notification(user, appointment, method="email")  # Default to email, adjust as needed
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