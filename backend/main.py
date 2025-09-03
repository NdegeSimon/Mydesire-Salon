
from backend.database import init_db, SessionLocal
from backend.models import User, Appointment, SalonAttendant
from backend.services.services import create_booking
from datetime import datetime

# Initialize DB and create tables
init_db()

# Open a DB session
session = SessionLocal()

try:
    # Check if user already exists
    existing_user = session.query(User).filter(User.email == "alice@example.com").first()
    if existing_user:
        user = existing_user
    else:
        # Add a user
        user = User(name="Alice", email="alice@example.com")
        user.set_password("password123")
        session.add(user)
        session.flush()  # Flush to get user ID
    
    # Check if attendant already exists
    existing_attendant = session.query(SalonAttendant).filter(SalonAttendant.email == "attendant@example.com").first()
    if existing_attendant:
        attendant = existing_attendant
    else:
        # Add a salon attendant
        attendant = SalonAttendant(name="John Doe", email="attendant@example.com")
        session.add(attendant)
        session.flush()  # Flush to get attendant ID
    
    session.commit()
    
    # Create appointment using the service
    create_booking(
        user_id=user.id,
        attendant_id=attendant.id,
        service="Haircut",
        time=datetime(2025, 9, 3, 15, 0)
    )
    
    print("User and appointment created!")
except Exception as e:
    session.rollback()
    print(f"Error: {e}")
finally:
    session.close()
