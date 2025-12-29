import uvicorn

if __name__ == "__main__":
    uvicorn.run(host='127.0.0.1',port=8001,app='app.main:app',reload=True)