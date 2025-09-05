from datetime import datetime
from backend.database import SessionLocal
from backend.models import User, SalonAttendant, Appointment, Notification
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Admin email (can be moved to environment variables)
ADMIN_EMAIL = "harrisonodongo@gmail.com"

# Email configuration (should be moved to environment variables in production)
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER", "your_email@gmail.com")  # Replace with actual email
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_app_password")  # Replace with actual app password

# Check if email credentials are properly configured
EMAIL_CONFIGURED = EMAIL_USER != "your_email@gmail.com" and EMAIL_PASSWORD != "your_app_password"

# ✅ Create booking with ORM
def create_booking(user_id, attendant_id, service, time):
    session = SessionLocal()
    try:
        # Create appointment
        appointment = Appointment(
            user_id=user_id,
            salon_attendant_id=attendant_id,
            service=service,
            appointment_time=time,
            status="pending"
        )
        session.add(appointment)
        session.flush()  # Flush to get the appointment ID

        # Send notification after booking
        message = f"Your booking for {service} with attendant {attendant_id} is confirmed for {time}."
        send_notification(session, user_id, message)
        
        # Send notification to admin
        admin_message = f"New booking: {service} for {time} by user {user_id}."
        send_admin_notification(admin_message, appointment, session)

        session.commit()
        print("✅ Booking created successfully!")
    except Exception as e:
        session.rollback()
        print("❌ Error creating booking:", e)
    finally:
        session.close()


# ✅ Send notification with ORM
def send_notification(session, user_id, message):
    # Save notification in DB
    notification = Notification(
        user_id=user_id,
        message=message,
        is_read=False
    )
    session.add(notification)
    session.flush()  # Flush to ensure notification is saved
    print(f"🔔 Notification saved to DB for user {user_id}: {message}")

    # Fetch customer info
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        print(f"📧 Sending email to {user.email}: {message}")
        # Send email to user (implementation needed)
        email_result = send_email(user.email, "Appointment Confirmation", message)
        if email_result:
            print(f"✅ Email sent successfully to {user.email}")
        else:
            print(f"❌ Failed to send email to {user.email}")
        # if you had phone numbers, same idea for SMS
    else:
        print(f"❌ User with ID {user_id} not found")

# ✅ Send notification to admin
def send_admin_notification(message, appointment, session):
    try:
        # Get user and attendant details
        user = session.query(User).filter_by(id=appointment.user_id).first()
        attendant = session.query(SalonAttendant).filter_by(id=appointment.salon_attendant_id).first()
        
        # Create detailed message
        detailed_message = f"""
New Appointment Booking
=======================

Service: {appointment.service}
Date & Time: {appointment.appointment_time}
Status: {appointment.status}

User Details:
Name: {user.name if user else 'Unknown'}
Email: {user.email if user else 'Unknown'}
Phone: {user.phone if user else 'Unknown'}

Attendant: {attendant.name if attendant else 'Unknown'}

Booking created at: {appointment.created_at}
        """.strip()
        
        print(f"📧 Sending admin notification to {ADMIN_EMAIL}: {message}")
        email_result = send_email(ADMIN_EMAIL, "New Appointment Booking - My Desire Salon", detailed_message)
        if email_result:
            print(f"✅ Admin notification email sent successfully to {ADMIN_EMAIL}")
        else:
            print(f"❌ Failed to send admin notification email to {ADMIN_EMAIL}")
    except Exception as e:
        print(f"❌ Error sending admin notification: {e}")

# ✅ Send email using SMTP
def send_email(to_email, subject, message):
    try:
        print(f"📧 Preparing to send email to {to_email} with subject '{subject}'")
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(message, 'plain'))
        
        # Create SMTP session
        print(f"📧 Connecting to SMTP server {EMAIL_HOST}:{EMAIL_PORT}")
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()  # Enable security
        print(f"📧 Logging in with user {EMAIL_USER}")
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {e}")
        return False
