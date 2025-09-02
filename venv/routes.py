from sqlalchemy.orm import Session
from models import User

def signup(session: Session, username: str, email: str, password: str):
    """
    Signup function using pure SQLAlchemy ORM (no Flask).
    session: SQLAlchemy Session object
    username, email, password: User details
    """

    # 1. Check if user exists
    existing_user = session.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        return {"error": "Username or email already exists"}

    # 2. Create new user
    new_user = User(username=username, email=email)
    new_user.set_password(password)  # assumes User has a set_password method

    # 3. Save to DB
    session.add(new_user)
    session.commit()

    return {"message": "User created successfully", "user_id": new_user.id}

def login(session: Session, username: str, password: str):
    """
    Login function using pure SQLAlchemy ORM (no Flask).
    session: SQLAlchemy Session object
    username, password: User credentials
    """

    # 1. Fetch user by username or email
    user = session.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()

    if not user:
        return {"error": "User not found"}

    # 2. Check password
    if not user.check_password(password):
        return {"error": "Invalid password"}

    return {"message": "Login successful", "user_id": user.id}