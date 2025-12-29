from fastapi import APIRouter,Depends
from app.schemas.user import UserSignup,UserLogin
from sqlalchemy.orm import Session
from app.services.v1.auth_services import create_user,verify_token,login,logout
from app.core.database import get_session
from app.utils.get_current_user import get_current_user

router = APIRouter()

@router.post('/signup')
async def signup(data:UserSignup,db:Session=Depends(get_session)):
    try:
        password = data.password
        email=data.email
        name=data.name

        return create_user(email,name,password,db)

    except Exception as e:
        raise e

@router.get('/verify-account')
async def verify_account(token:str,db:Session=Depends(get_session)):
    try:
        return verify_token(str(token),db=db)
    
    except Exception as e:
        print(e)
        raise e

@router.post('/login')
async def login_account(payload:UserLogin,db:Session=Depends(get_session)):
    try:
        return login(payload.email,payload.password,db=db)
    except Exception as e:
        print(e)
        raise e

@router.get('/logout')
async def logout_current_user(current_user=Depends(get_current_user),db:Session=Depends(get_session)):
    try:
        return logout(user_id=str(current_user.id),db=db)
    except Exception as e:
        print(e)
        raise e