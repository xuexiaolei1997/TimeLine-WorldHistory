from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.database import db_manager
from models import Base
from core.exceptions import add_exception_handlers
from endpoints import events, periods
from admin import setup_admin
import os
from dotenv import load_dotenv

load_dotenv()

# Create tables
Base.metadata.create_all(bind=db_manager.engine)

app = FastAPI()

# Add exception handlers
add_exception_handlers(app)

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events.router)
app.include_router(periods.router)

# Admin setup
@app.on_event("startup")
async def startup():
    await setup_admin()

@app.get("/")
def read_root():
    return {"message": "World History Timeline API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
