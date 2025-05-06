from sqlalchemy import Column, Integer, String, JSON
from .base import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    location = Column(JSON)
    zoom_level = Column(Integer)
