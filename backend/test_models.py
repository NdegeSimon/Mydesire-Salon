from models import User, login, session, Base, engine
import os

if __name__ == "__main__":
    # Clear existing data and recreate tables (for a clean test)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Test Signup
    print("Testing Signup...")
    assert User.signup("Alice", "alice@example.com", "123-456-7890", "securepass123") == True, "Signup failed for Alice"
    assert User.signup("Bob", "bob@example.com", "098-765-4321", "anotherpass456") == True, "Signup failed for Bob"
    assert User.signup("Alice", "alice@example.com", "111-222-3333", "newpass789") == False, "Duplicate email should fail"
    print("Signup tests passed!")

    # Test Login
    print("Testing Login...")
    assert login("alice@example.com", "securepass123") == True, "Login failed for Alice with correct password"
    assert login("alice@example.com", "wrongpass") == False, "Login should fail with wrong password"
    assert login("bob@example.com", "anotherpass456") == True, "Login failed for Bob with correct password"
    assert login("nonexistent@example.com", "anypass") == False, "Login should fail for nonexistent user"
    print("Login tests passed!")

    # Verify data in database (optional)
    user = session.query(User).filter_by(email="alice@example.com").first()
    if user:
        print(f"User found: {user.name}, Password hash: {user.password_hash}")
    else:
        print("User not found in database!")

    # Clean up
    session.close()