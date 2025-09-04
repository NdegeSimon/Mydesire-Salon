from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash

# Set up SQLAlchemy
Base = declarative_base()
engine = create_engine('sqlite:///users.db', echo=True)  # Replace with your DB URL
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(255), nullable=False)  # Added phone column
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete")
    payments = relationship("Payments", back_populates="user", cascade="all, delete")
    reviews = relationship("Reviews", back_populates="user", cascade="all, delete")
    
    def __init__(self, name, email, phone, password=None):
        self.name = name
        self.email = email
        self.phone = phone
        if password:
            self.set_password(password)

    def set_password(self, password):
        """Hash and set the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the password against the stored hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @classmethod
    def find_by_email(cls, email):
        """Find a user by email."""
        return session.query(cls).filter_by(email=email).first()

    @classmethod
    def signup(cls, name, email, phone, password):
        """Handle user signup."""
        if cls.find_by_email(email):
            print("Email already registered!")
            return False
        
        new_user = cls(name, email, phone, password)
        session.add(new_user)
        session.commit()
        print(f"User {name} signed up successfully!")
        return True

def login(email, password):
    """Handle user login."""
    user = User.find_by_email(email)
    if user and user.check_password(password):
        print(f"Login successful for {user.name}!")
        return True
    else:
        print("Invalid email or password!")
        return False

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    salon_attendant_id = Column(Integer, ForeignKey("salon_attendants.id"), nullable=False)
    service = Column(String(255), nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="appointments")
    salon_attendant = relationship("SalonAttendant", back_populates="appointments")
    payments = relationship("Payments", back_populates="appointment", cascade="all, delete")
    reviews = relationship("Reviews", back_populates="appointment", cascade="all, delete")

class SalonAttendant(Base):
    __tablename__ = 'salon_attendants'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    appointments = relationship("Appointment", back_populates="salon_attendant", cascade="all, delete")
    reviews = relationship("Reviews", back_populates="salon_attendant", cascade="all, delete")

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="notifications")

class Payments(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="payments")
    appointment = relationship("Appointment", back_populates="payments")

class Reviews(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    salon_attendant_id = Column(Integer, ForeignKey("salon_attendants.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    appointment = relationship("Appointment", back_populates="reviews")
    salon_attendant = relationship("SalonAttendant", back_populates="reviews")

# Create the database tables
Base.metadata.create_all(engine)