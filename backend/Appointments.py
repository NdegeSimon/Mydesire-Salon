from datetime import datetime, timezone, timedelta
from backend.database import SessionLocal
from backend.models import User, SalonAttendant, Appointment, Notification
from services import SEND_EMAIL  # Import send_email from services.py
import os
from dotenv import load_dotenv
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Time zone for EAT (UTC+3)
EAT = timezone(timedelta(hours=3))

# Email configuration
EMAIL_USER = os.getenv("EMAIL_USER", "simopetley@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "oifq dfhf kdhw itbz")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "harrisonodongo@gmail.com")
EMAIL_CONFIGURED = bool(EMAIL_USER and EMAIL_PASSWORD)

# Twilio configuration
TWILIO_CONFIGURED = bool(
    os.getenv("TWILIO_ACCOUNT_SID") and
    os.getenv("TWILIO_AUTH_TOKEN") and
    os.getenv("TWILIO_PHONE_NUMBER") and
    os.getenv("ADMIN_PHONE")
)

def create_appointment(user_email, salon_attendant_id, service, appointment_time, contact_method="email"):
    """
    Create a new appointment for a user.

    Args:
        user_email (str): The email of the user making the appointment.
        salon_attendant_id (int): The ID of the salon attendant.
        service (str): The service to be provided.
        appointment_time (datetime): The scheduled time of the appointment.
        contact_method (str, optional): The user's preferred contact method (email, sms). Defaults to "email".

    Returns:
        Appointment or str: The created appointment object, or an error message if failed.
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(email=user_email).first()
        if not user:
            logger.warning(f"User with email {user_email} not found")
            return "Please log in to make an appointment."

        if not session.query(SalonAttendant).filter_by(id=salon_attendant_id).first():
            logger.warning(f"Salon attendant with ID {salon_attendant_id} not found")
            return "Salon attendant not found."

        new_appointment = Appointment(
            user_id=user.id,
            salon_attendant_id=salon_attendant_id,
            service=service,
            appointment_time=appointment_time,
            status="pending",
            created_at=datetime.now(EAT)
        )
        session.add(new_appointment)
        session.flush()

        # Send user notification
        send_notification(session, user, new_appointment, contact_method)

        # Send admin notification
        send_admin_notification(new_appointment, session)

        session.commit()
        logger.info(f"Appointment created for {user.name} at {appointment_time.astimezone(EAT).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        return new_appointment
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating appointment for {user_email}: {e}")
        return f"Failed to create appointment: {e}"
    finally:
        session.close()

def send_notification(session, user, appointment, method="email"):
    """
    Send a notification (email or SMS) about an appointment and save it to the database.

    Args:
        session: SQLAlchemy session.
        user (User): The user object.
        appointment (Appointment): The appointment object.
        method (str): The contact method (email, sms). Defaults to "email".

    Returns:
        bool: True if notification sent successfully, False otherwise.
    """
    message = f"Dear {user.name}, Your appointment for {appointment.service} at {appointment.appointment_time.astimezone(EAT).strftime('%Y-%m-%d %H:%M:%S %Z')} is {appointment.status}."
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>My Desire Salon - Appointment Confirmation</h2>
            <p>{message}</p>
            <p>Thank you for choosing My Desire Salon!</p>
        </body>
    </html>
    """

    # Save notification to database
    try:
        notification = Notification(
            user_id=user.id,
            message=message,
            is_read=False,
            created_at=datetime.now(EAT)
        )
        session.add(notification)
        session.flush()
        logger.info(f"Notification saved to DB for user {user.id}: {message}")
    except Exception as e:
        logger.error(f"Error saving notification for user {user.id}: {e}")
        return False

    if method == "email":
        if user.email:
            return send_email(user.email, "Appointment Confirmation - My Desire Salon", html_message, is_html=True)
        else:
            logger.warning(f"No email found for user {user.id}")
            return False
    elif method == "sms" and TWILIO_CONFIGURED:
        if user.phone:
            try:
                client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
                sms = client.messages.create(
                    body=message,
                    from_=os.getenv("TWILIO_PHONE_NUMBER"),
                    to=user.phone
                )
                logger.info(f"SMS sent to {user.phone}: {sms.sid}")
                return True
            except TwilioRestException as e:
                logger.error(f"SMS failed for {user.phone}: {e}")
                return False
        else:
            logger.warning(f"No phone found for user {user.id}")
            return False
    else:
        logger.warning(f"Unsupported or unconfigured contact method: {method}")
        return False

def send_admin_notification(appointment, session):
    """
    Send notification to admin about an appointment.

    Args:
        appointment (Appointment): The appointment object.
        session: SQLAlchemy session.
    """
    try:
        user = session.query(User).filter_by(id=appointment.user_id).first()
        attendant = session.query(SalonAttendant).filter_by(id=appointment.salon_attendant_id).first()
        
        detailed_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>New Appointment Booking - My Desire Salon</h2>
                <p><strong>Service:</strong> {appointment.service}</p>
                <p><strong>Date & Time:</strong> {appointment.appointment_time.astimezone(EAT).strftime('%Y-%m-%d %H:%M:%S %Z')}</p>
                <p><strong>Status:</strong> {appointment.status}</p>
                <p><strong>User:</strong> {user.name if user else 'Unknown'} ({user.email if user else 'Unknown'})</p>
                <p><strong>Phone:</strong> {user.phone if user else 'Unknown'}</p>
                <p><strong>Attendant:</strong> {attendant.name if attendant else 'Unknown'}</p>
                <p><strong>Booked at:</strong> {appointment.created_at.astimezone(EAT).strftime('%Y-%m-%d %H:%M:%S %Z')}</p>
            </body>
        </html>
        """
        send_email(ADMIN_EMAIL, "New Appointment Booking - My Desire Salon", detailed_message, is_html=True)
        
        if TWILIO_CONFIGURED:
            try:
                client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
                sms = client.messages.create(
                    body=f"New booking: {appointment.service} at {appointment.appointment_time.astimezone(EAT).strftime('%Y-%m-%d %H:%M:%S %Z')}",
                    from_=os.getenv("TWILIO_PHONE_NUMBER"),
                    to=os.getenv("ADMIN_PHONE")
                )
                logger.info(f"SMS sent to {os.getenv('ADMIN_PHONE')}: {sms.sid}")
            except TwilioRestException as e:
                logger.error(f"Error sending SMS to admin: {e}")
    except Exception as e:
        logger.error(f"Error sending admin notification: {e}")

def update_appointment_status(appointment_id, new_status, contact_method="email"):
    """
    Update the status of an appointment and send a notification.

    Args:
        appointment_id (int): The ID of the appointment.
        new_status (str): The new status (e.g., "confirmed", "completed", "canceled").
        contact_method (str, optional): The user's preferred contact method (email, sms). Defaults to "email".

    Returns:
        bool: True if successful, False otherwise.
    """
    session = SessionLocal()
    try:
        appointment = session.query(Appointment).filter_by(id=appointment_id).first()
        if not appointment:
            logger.warning(f"Appointment {appointment_id} not found")
            return False

        appointment.status = new_status
        session.flush()

        user = session.query(User).filter_by(id=appointment.user_id).first()
        if user:
            send_notification(session, user, appointment, contact_method)
        send_admin_notification(appointment, session)
        
        session.commit()
        logger.info(f"Appointment {appointment_id} status updated to {new_status} at {datetime.now(EAT).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating appointment {appointment_id}: {e}")
        return False
    finally:
        session.close()

def get_user_appointments(user_email):
    """
    Retrieve all appointments for a user.

    Args:
        user_email (str): The email of the user.

    Returns:
        list: List of appointment dictionaries.
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(email=user_email).first()
        if not user:
            logger.warning(f"User with email {user_email} not found")
            return []

        appointments = session.query(Appointment).filter_by(user_id=user.id).all()
        return [
            {
                "id": appt.id,
                "service": appt.service,
                "appointment_time": appt.appointment_time.astimezone(EAT).strftime('%Y-%m-%d %H:%M:%S %Z'),
                "status": appt.status,
                "attendant_id": appt.salon_attendant_id,
                "created_at": appt.created_at.astimezone(EAT).strftime('%Y-%m-%d %H:%M:%S %Z')
            }
            for appt in appointments
        ]
    except Exception as e:
        logger.error(f"Error retrieving appointments for {user_email}: {e}")
        return []
    finally:
        session.close()

if __name__ == "__main__":
    # Create test data
    session = SessionLocal()
    user = User(name="John Doe", email="client@example.com", phone="+254123456789")
    attendant = SalonAttendant(name="Jane Smith")
    session.add_all([user, attendant])
    session.commit()
    user_email = user.email
    attendant_id = attendant.id
    session.close()

    # Test appointment creation
    appointment_time = datetime(2025, 9, 7, 14, 0, tzinfo=EAT)
    result = create_appointment(user_email, attendant_id, "Haircut", appointment_time, contact_method="email")
    if isinstance(result, Appointment):
        logger.info(f"Created appointment with ID {result.id}")
        # Test status update
        update_appointment_status(result.id, "confirmed", contact_method="email")
        # Test retrieving appointments
        appointments = get_user_appointments(user_email)
        logger.info(f"User appointments: {appointments}")
    else:
        logger.error(f"Appointment creation failed: {result}")