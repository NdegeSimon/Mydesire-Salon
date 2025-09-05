from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.models import Base, SalonAttendant
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///users.db')

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    # Seed initial attendants if none exist
    session = SessionLocal()
    try:
        if session.query(SalonAttendant).count() == 0:
            sample_attendants = [
                SalonAttendant(name="Harrison", email="harrison@mydesiresalon.com"),
                SalonAttendant(name="Maria Rodriguez", email="maria@mydesiresalon.com"),
                SalonAttendant(name="Ashley Kim", email="ashley@mydesiresalon.com"),
                SalonAttendant(name="Jennifer White", email="jennifer@mydesiresalon.com"),
            ]
            session.add_all(sample_attendants)
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
