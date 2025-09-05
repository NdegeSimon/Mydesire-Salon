#!/usr/bin/env python3
"""
Test script for My Desire Salon Application
This script tests the main components of the application.
"""

import sys
import os
import time
import requests

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_backend_api():
    """Test if the backend API is running and responding."""
    print("Testing backend API...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✓ Backend API is running")
            return True
        else:
            print("✗ Backend API returned status code:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Backend API is not accessible. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print("✗ Error testing backend API:", str(e))
        return False

def test_database_connection():
    """Test if the database is accessible."""
    print("Testing database connection...")
    try:
        from backend.database import SessionLocal
        from backend.models import User, SalonAttendant
        
        db = SessionLocal()
        try:
            # Try to query the database
            user_count = db.query(User).count()
            attendant_count = db.query(SalonAttendant).count()
            print(f"✓ Database connection successful")
            print(f"  - Users in database: {user_count}")
            print(f"  - Attendants in database: {attendant_count}")
            return True
        finally:
            db.close()
    except Exception as e:
        print("✗ Error testing database connection:", str(e))
        return False

def test_user_signup():
    """Test user signup functionality."""
    print("Testing user signup...")
    try:
        from backend.models import User
        
        # Test signup with a new user
        result = User.signup("Test User 3", "test3@example.com", "1234567892", "testpassword")
        if result:
            print("✓ User signup successful")
            return True
        else:
            print("✗ User signup failed")
            return False
    except Exception as e:
        print("✗ Error testing user signup:", str(e))
        return False

def test_user_login():
    """Test user login functionality."""
    print("Testing user login...")
    try:
        from backend.models import User
        
        # Test login with the test user
        result = User.find_by_email("test3@example.com")
        if result:
            login_result = result.check_password("testpassword")
            if login_result:
                print("✓ User login successful")
                return True
            else:
                print("✗ User login failed - incorrect password")
                return False
        else:
            print("✗ User not found for login test")
            return False
    except Exception as e:
        print("✗ Error testing user login:", str(e))
        return False

def test_create_appointment():
    """Test appointment creation functionality."""
    print("Testing appointment creation...")
    try:
        from backend.Appointments import create_appointment
        from datetime import datetime
        
        # Create a test appointment
        appointment_time = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)
        result = create_appointment(
            "test3@example.com",
            1,  # Assuming attendant ID 1 exists
            "Haircut",
            appointment_time
        )
        
        if result and not isinstance(result, str):
            print("✓ Appointment creation successful")
            return True
        else:
            print("✗ Appointment creation failed:", result if isinstance(result, str) else "Unknown error")
            return False
    except Exception as e:
        print("✗ Error testing appointment creation:", str(e))
        return False

def main():
    """Main test function."""
    print("My Desire Salon Application Test Suite")
    print("=" * 40)
    
    # Run all tests
    tests = [
        test_database_connection,
        test_backend_api,
        test_user_signup,
        test_user_login,
        test_create_appointment
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {str(e)}")
            results.append(False)
            print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the application setup.")
    
    return passed == total

if __name__ == "__main__":
    main()