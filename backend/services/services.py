from datetime import datetime
from backend.database import SessionLocal
from backend.models import User, SalonAttendant, Appointment, Notification


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

    # Fetch customer info
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        print(f"📧 Sending email to {user.email}: {message}")
        # if you had phone numbers, same idea for SMS
