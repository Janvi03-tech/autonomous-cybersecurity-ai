from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String)
    source_ip = Column(String)
    destination_ip = Column(String)
    username = Column(String)
    severity = Column(String)
    risk_score = Column(Integer)
    raw_log = Column(Text)