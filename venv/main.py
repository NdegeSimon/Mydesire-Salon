
from database import init_db, SessionLocal
from models import User, Appointment
from datetime import datetime

# Initialize DB and create tables
init_db()

# Open a DB session
session = SessionLocal()

# Add a user
new_user = User(username="Alice", email="alice@example.com")
new_user.set_password("password123")
session.add(new_user)
session.commit()
# Add appointment for Alice
appointment = Appointment(
    user_id=new_user.id,
    service="Haircut",
    appointment_time=datetime(2025, 9, 3, 15, 0)
)
session.add(appointment)
session.commit()

print("User and appointment created!")
