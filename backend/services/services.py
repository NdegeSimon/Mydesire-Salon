from datetime import datetime, timezone, timedelta
from backend.database import SessionLocal
from backend.models import User, SalonAttendant, Appointment, Notification
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER", "simopetley@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "oifq dfhf kdhw itbz")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "harrisonodongo@gmail.com")

# Check if email credentials are properly configured
EMAIL_CONFIGURED = bool(EMAIL_USER and EMAIL_PASSWORD)

# Twilio configuration
TWILIO_CONFIGURED = bool(
    os.getenv("TWILIO_ACCOUNT_SID") and
    os.getenv("TWILIO_AUTH_TOKEN") and
    os.getenv("TWILIO_PHONE_NUMBER") and
    os.getenv("ADMIN_PHONE")
)

def send_email(to_email, subject, message, is_html=False):
    """Send an email using SMTP."""
    if not EMAIL_CONFIGURED:
        logger.error("Email not configured. Check EMAIL_USER and EMAIL_PASSWORD in .env.")
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'html' if is_html else 'plain'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()
        logger.info(f"Email sent to {to_email} at {datetime.now(EAT).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        return True
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")
        return False

def create_booking(user_id, attendant_id, service, time):
    """Create a booking and send notifications."""
    session = SessionLocal()
    try:
        # Create appointment
        appointment = Appointment(
            user_id=user_id,
            salon_attendant_id=attendant_id,
            service=service,
            appointment_time=time,
            status="pending",
            created_at=datetime.now(EAT)
        )
        session.add(appointment)
        session.flush()

        # Send user notification
        message = f"Your booking for {service} with attendant {attendant_id} is confirmed for {time.astimezone(EAT).strftime('%Y-%m-%d %H:%M:%S %Z')}."
        send_notification(session, user_id, message)

        # Send admin notification
        admin_message = f"New booking: {service} for {time.astimezone(EAT).strftime('%Y-%m-%d %H:%M:%S %Z')} by user {user_id}."
        send_admin_notification(admin_message, appointment, session)

        session.commit()
        logger.info(f"Booking created successfully at {datetime.now(EAT).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating booking: {e}")
    finally:
        session.close()

def send_notification(session, user_id, message):
    """Save and send notification to user."""
    try:
        # Save notification in DB
        notification = Notification(
            user_id=user_id,
            message=message,
            is_read=False,
            created_at=datetime.now(EAT)
        )
        session.add(notification)
        session.flush()
        logger.info(f"Notification saved to DB for user {user_id}: {message}")

        # Fetch user
        user = session.query(User).filter_by(id=user_id).first()
        if user and user.email:
            html_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>My Desire Salon - Appointment Confirmation</h2>
                    <p>{message}</p>
                    <p>Thank you for choosing My Desire Salon!</p>
                </body>
            </html>
            """
            send_email(user.email, "Appointment Confirmation - My Desire Salon", html_message, is_html=True)
        else:
            logger.warning(f"No email found for user {user_id}")
    except Exception as e:
        logger.error(f"Error sending notification for user {user_id}: {e}")

def send_admin_notification(message, appointment, session):
    """Send notification to admin."""
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

def get_user_notifications(session, user_id):
    """Retrieve notifications for a user."""
    try:
        notifications = session.query(Notification).filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
        return [
            {
                "id": notification.id,
                "message": notification.message,
                "is_read": notification.is_read,
                "created_at": notification.created_at.astimezone(EAT).strftime('%Y-%m-%d %H:%M:%S %Z') if notification.created_at else None
            }
            for notification in notifications
        ]
    except Exception as e:
        logger.error(f"Error retrieving notifications for user {user_id}: {e}")
        return []

def send_reminders():
    """Send reminders for upcoming appointments."""
    session = SessionLocal()
    try:
        now = datetime.now(EAT)
        tomorrow = now + timedelta(days=1)
        appointments = session.query(Appointment).filter(
            Appointment.appointment_time.between(now, tomorrow),
            Appointment.status == "pending"
        ).all()
        for appt in appointments:
            user = session.query(User).filter_by(id=appt.user_id).first()
            if user and user.email:
                message = f"Reminder: Your {appt.service} appointment is scheduled for {appt.appointment_time.astimezone(EAT).strftime('%Y-%m-%d %H:%M:%S %Z')}."
                html_message = f"""
                <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h2>My Desire Salon - Appointment Reminder</h2>
                        <p>{message}</p>
                        <p>Thank you for choosing My Desire Salon!</p>
                    </body>
                </html>
                """
                send_email(user.email, "Appointment Reminder - My Desire Salon", html_message, is_html=True)
            
            admin_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>My Desire Salon - Appointment Reminder</h2>
                    <p><strong>Service:</strong> {appt.service}</p>
                    <p><strong>Date & Time:</strong> {appt.appointment_time.astimezone(EAT).strftime('%Y-%m-%d %H:%M:%S %Z')}</p>
                    <p><strong>User ID:</strong> {appt.user_id}</p>
                </body>
            </html>
            """
            send_email(ADMIN_EMAIL, "Appointment Reminder - My Desire Salon", admin_message, is_html=True)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error sending reminders: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Create test data
    session = SessionLocal()
    user = User(name="John Doe", email="client@example.com", phone="+254123456789")
    attendant = SalonAttendant(name="Jane Smith")
    session.add_all([user, attendant])
    session.commit()
    user_id = user.id
    attendant_id = attendant.id
    session.close()

    # Create a test booking
    create_booking(user_id, attendant_id, "Haircut", datetime(2025, 9, 7, 14, 0, tzinfo=EAT))