from sqlalchemy import Column, Integer, String
from .base import Base

class Period(Base):
    __tablename__ = "periods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    start_year = Column(Integer)
    end_year = Column(Integer)
    color = Column(String)
