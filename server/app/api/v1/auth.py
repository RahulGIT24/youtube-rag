from fastapi import APIRouter,Depends
from app.schemas.user import UserSignup
from sqlalchemy.orm import Session
from app.services.v1.auth_services import create_user,verify_token
from app.core.database import get_session

router = APIRouter()

@router.post('/signup')
async def signup(data:UserSignup,db:Session=Depends(get_session)):
    try:
        password = data.password
        email=data.email
        name=data.name

        return create_user(email,name,password,db)

    except Exception as e:
        print(e)
        raise e

@router.get('/verify-account')
async def verify_account(token:str,db:Session=Depends(get_session)):
    try:
        return verify_token(str(token),db=db)
    except Exception as e:
        print(e)
        raise e
