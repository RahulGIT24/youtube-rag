import uvicorn
from alembic import command
from alembic.config import Config

if __name__ == "__main__":
    # Run Alembic migrations
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")  # applies all pending migrations

    # Start FastAPI
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)