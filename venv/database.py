from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///users.db')

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # will store hash
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete")

class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service = Column(String(255), nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    user = relationship("User", back_populates="appointments")

if __name__ == "__main__":
    engine = create_engine(DATABASE_URL, echo=True)  # echo logs SQL queries
    Base.metadata.create_all(engine)
