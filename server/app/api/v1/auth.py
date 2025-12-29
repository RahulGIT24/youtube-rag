from fastapi import APIRouter,Depends
from app.schemas.user import UserSignup
from sqlalchemy.orm import Session
from app.services.v1.auth_services import create_user
from app.core.database import get_session

router = APIRouter()

@router.post('/signup')
def signup(data:UserSignup,db:Session=Depends(get_session)):
    try:
        password = data.password
        email=data.email
        name=data.name

        return create_user(email,name,password,db)

    except Exception as e:
        print(e)
        raise e
