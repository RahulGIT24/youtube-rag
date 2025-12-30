from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
import jwt
from core.database import get_session
from core.config import settings
from models.user import User

def get_current_user(request: Request, db: Session = Depends(get_session)):
    """
    Extracts the 'access_token' from cookies, validates it, 
    and returns the User object.
    """
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated (No token found)",
        )

    try:
        payload = jwt.decode(
            token, 
            str(settings.ACCESS_TOKEN_SECRET), 
            algorithms=["HS256"]
        )
        
        user_id: str = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user