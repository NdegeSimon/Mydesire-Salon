from sqlalchemy.orm import Session
from backend.models import User

def signup(session: Session, name: str, email: str, phone: str, password: str):
    """
    Signup function using pure SQLAlchemy ORM (no Flask).
    session: SQLAlchemy Session object
    name, email, password: User details
    """

    # 1. Check if user exists
    existing_user = session.query(User).filter(
        (User.name == name) | (User.email == email)
    ).first()

    if existing_user:
        return {"error": "Name or email already exists"}

    # 2. Create new user
    new_user = User(name=name, email=email, phone=phone)
    new_user.set_password(password)  # assumes User has a set_password method

    # 3. Save to DB
    session.add(new_user)
    session.commit()

    return {"message": "User created successfully", "user_id": new_user.id}

def login(session: Session, identifier: str, password: str):
    """
    Login function using pure SQLAlchemy ORM (no Flask).
    session: SQLAlchemy Session object
    identifier, password: User credentials (identifier can be name or email)
    """

    # 1. Fetch user by name or email
    user = session.query(User).filter(
        (User.name == identifier) | (User.email == identifier)
    ).first()

    if not user:
        return {"error": "User not found"}

    # 2. Check password
    if not user.check_password(password):
        return {"error": "Invalid password"}

    return {"message": "Login successful", "user_id": user.id}