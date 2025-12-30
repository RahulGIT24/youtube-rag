from fastapi import APIRouter,Depends,HTTPException
from core.database import get_session
from app.utils.get_current_user import get_current_user
from app.schemas.transcribe import UserQuery
from sqlalchemy.orm import Session
from app.services.v1.transcribe import generate_response

router = APIRouter()

@router.post('/')
async def chat(data:UserQuery,session_id:int,db:Session=Depends(get_session),user=Depends(get_current_user)):
    user_id = user.id
    query = data.query

    if not session_id:
        raise HTTPException(detail="Please provide session id",status_code=406)
    if len(query) < 20:
        raise HTTPException(detail="Query Should be more than 20 characters",status_code=406)
    if len(query) > 500:
        raise HTTPException(detail="Query Should not exceed 500 characters",status_code=406)

    return generate_response(db=db,query=query,session_id=session_id,user_id=user_id)
