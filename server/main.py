from fastapi import FastAPI
import uvicorn
from api.router import api_router
from core.config import settings

app = FastAPI()

@app.get('/')
def health_check():
    return {"message":"Server is healthy"}

app.include_router(api_router,prefix=settings.API_V1_PREFIX)

if __name__ == "__main__":
    uvicorn.run(host='127.0.0.1',port=8001,app='main:app',reload=True)