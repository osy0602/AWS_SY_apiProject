import uuid
from sqlalchemy import Column, String, INT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Jikgu(Base):
    __tablename__ = 'jikgu'
    id = Column(String(120), primary_key=True)
    year = Column(INT, unique=False, nullable=False)
    subject = Column(String(255), unique=True, nullable=False)
    purchase = Column(INT, unique=False, nullable=False)
    percentage = Column(INT, unique=False, nullable=False)

