#!/usr/bin/env python3
"""
Startup script for My Desire Salon Application
This script initializes the database and starts the FastAPI backend server.
"""

import os
import sys
import subprocess
import time
from backend.database import init_db, SessionLocal
from backend.models import User, SalonAttendant

def initialize_database():
    """Initialize the database and add sample data if needed."""
    print("Initializing database...")
    init_db()
    
    # Create a session to add sample data
    db = SessionLocal()
    
    try:
        # Check if we have any attendants, if not add sample ones
        attendants = db.query(SalonAttendant).all()
        if not attendants:
            print("Adding sample salon attendants...")
            sample_attendants = [
                SalonAttendant(name="Harrison", email="harrison@mydesiresalon.com"),
                SalonAttendant(name="Maria Rodriguez", email="maria@mydesiresalon.com"),
                SalonAttendant(name="Ashley Kim", email="ashley@mydesiresalon.com"),
                SalonAttendant(name="Jennifer White", email="jennifer@mydesiresalon.com")
            ]
            
            for attendant in sample_attendants:
                existing = db.query(SalonAttendant).filter(SalonAttendant.email == attendant.email).first()
                if not existing:
                    db.add(attendant)
            
            db.commit()
            print("Sample attendants added successfully!")
        
        # Check if we have any users, if not add a sample one
        users = db.query(User).all()
        if not users:
            print("Adding sample user...")
            sample_user = User(name="Alice", email="alice@example.com", phone="1234567890")
            sample_user.set_password("password123")
            
            existing = db.query(User).filter(User.email == sample_user.email).first()
            if not existing:
                db.add(sample_user)
                db.commit()
                print("Sample user added successfully!")
                print("Default login credentials:")
                print("  Email: alice@example.com")
                print("  Password: password123")
                
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

def start_backend():
    """Start the FastAPI backend server."""
    print("Starting FastAPI backend server...")
    try:
        # Use uvicorn to run the FastAPI app
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "backend.api:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        print("FastAPI backend server started on http://localhost:8000")
        return backend_process
    except Exception as e:
        print(f"Error starting backend server: {e}")
        return None

def main():
    """Main function to start the application."""
    print("Starting My Desire Salon Application...")
    
    # Initialize database
    initialize_database()
    
    # Start backend server
    backend_process = start_backend()
    
    if backend_process:
        print("\nMy Desire Salon Application is now running!")
        print("Backend API: http://localhost:8000")
        print("Frontend: Open index.html in your browser")
        print("\nPress Ctrl+C to stop the application.")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down My Desire Salon Application...")
            backend_process.terminate()
            backend_process.wait()
            sys.exit(0)
    else:
        print("Failed to start the application.")
        sys.exit(1)

if __name__ == "__main__":
    main()