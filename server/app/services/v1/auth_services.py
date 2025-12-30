from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.user import User
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from datetime import datetime,timedelta,timezone
from core.redis import redis_client
import json
import jwt
from core.config import settings
from models import User

EMAIL_QUEUE="queue:email"
EMAIL_AGAIN_MINUTES = 15
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def generate_verification_token(user_id:str,expire_minutes: int = 30):
    to_encode = {"sub": str(user_id)} 
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire, "iat": datetime.now(tz=timezone.utc)})
    
    encoded_jwt = jwt.encode(to_encode, settings.VERIFICATION_SECRET_KEY, algorithm='HS256')
    return encoded_jwt

def generate_access_token(user_id:str,email:str):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": int((datetime.now(tz=timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "iat": int(datetime.now(tz=timezone.utc).timestamp())
    }
    encoded_jwt = jwt.encode(payload, settings.ACCESS_TOKEN_SECRET, algorithm='HS256')
    return encoded_jwt

def generate_refresh_token(user_id:str):
    payload = {
        "user_id": user_id,
        "exp": int((datetime.now(tz=timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "iat": int(datetime.now(tz=timezone.utc).timestamp())
    }

    encoded_jwt = jwt.encode(payload, settings.REFRESH_TOKEN_SECRET, algorithm='HS256')
    return encoded_jwt

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

            token=generate_verification_token(user_id=existing_user.id)
            existing_user.name = name
            existing_user.password = get_password_hash(password)
            existing_user.verification_token_sent_at = now
            existing_user.verification_token=token

            db.commit()
            db.refresh(existing_user)
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

        new_user.verification_token = token

        db.commit()
        db.refresh(new_user)
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

def verify_token(token:str,db:Session):
    try:
        decoded_payload = jwt.decode(token,settings.VERIFICATION_SECRET_KEY,'HS256')
        user_id=decoded_payload['sub']

        user = db.query(User).filter(User.id==int(user_id)).first()

        user.is_verified = True
        user.verification_token = None
        user.verification_token_sent_at = None

        db.commit()
        db.refresh(user)

        return JSONResponse(content={"message":"User Verified. You can login now."},status_code=200)
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(detail="Token Expired",status_code=403)
    except jwt.InvalidTokenError as e:
        raise HTTPException(detail="Invalid Token",status_code=403)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

def login(email:str,password:str,db:Session):
    try:
        user =  db.query(User).filter(User.email==email,User.is_verified==True).first()

        if not user:
            raise HTTPException(detail="User not found or not verified. Please register from Signup Form",status_code=404)

        is_valid = verify_password(hashed_password=user.password,plain_password=password)

        if not is_valid:
            raise HTTPException(detail="Invalid Credentials",status_code=401)

        access_token = generate_access_token(email=user.email,user_id=str(user.id))
        refresh_token = generate_refresh_token(user_id=str(user.id))

        user.refresh_token = refresh_token
        db.commit()
        db.refresh(user)

        response = JSONResponse(
            content={"message":"Login Successfull"},
            status_code=200
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

def logout(user_id: str, db: Session):
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user:
            user.refresh_token = None
            db.commit()
            db.refresh(user)

        response = JSONResponse(
            content={"message": "Logout Successful"}, 
            status_code=200
        )

        response.delete_cookie(key="access_token", httponly=True, secure=True, samesite='lax')
        response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite='lax')

        return response

    except Exception as e:
        print(f"Logout Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")