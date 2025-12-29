from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from datetime import datetime,timedelta,timezone
from app.core.redis import redis_client
import json
import jwt
from app.core.config import settings

EMAIL_QUEUE="queue:email"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def generate_verification_token(user_id:int,expire_minutes: int = 30):
    to_encode = {"sub": user_id} 
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire, "iat": datetime.now(tz=timezone.utc)})
    
    encoded_jwt = jwt.encode(to_encode, settings.VERIFICATION_SECRET_KEY, algorithm='HS256')
    return encoded_jwt

EMAIL_AGAIN_MINUTES = 15

def create_user(email: str, name: str, password: str, db: Session):
    try:
        existing_user = db.query(User).filter(User.email == email).first()
        now = datetime.now(timezone.utc)

        if existing_user:
            if existing_user.is_verified:
                raise HTTPException(status_code=409, detail="User already exists")

            if existing_user.verification_token_sent_at:
                if now - existing_user.verification_token_sent_at < timedelta(minutes=EMAIL_AGAIN_MINUTES):
                    return JSONResponse(
                        content={"message": "Verification email already sent. Please wait."},
                        status_code=200
                    )

            existing_user.name = name
            existing_user.password = get_password_hash(password)
            existing_user.verification_token_sent_at = now

            db.commit()
            db.refresh(existing_user)
            token=generate_verification_token(user_id=existing_user.id)
            details = {
                "name": name,
                "email": email,
                "token":token,
                "type": "signup"
            }
            redis_client.lpush(EMAIL_QUEUE, json.dumps(details))

            return JSONResponse(
                content={"message": "Verification email resent"},
                status_code=202
            )

        # create new user
        new_user = User(
            name=name,
            email=email,
            password=get_password_hash(password),
            verification_token_sent_at=now,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        token=generate_verification_token(user_id=new_user.id)

        details = {
            "name": name,
            "email": email,
            "token":token,
            "type": "signup"
        }
        redis_client.lpush(EMAIL_QUEUE, json.dumps(details))

        return JSONResponse(
            content={"message": "User created. Verification email sent"},
            status_code=201
        )

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

