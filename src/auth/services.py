from fastapi import HTTPException, status
from src.auth.models import User


def find_user_by_username(db, username):
    user =  db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user