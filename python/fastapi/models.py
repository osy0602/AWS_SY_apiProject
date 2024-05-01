import uuid
from sqlalchemy import Column, String, INT, BLOB, FLOAT, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Jikgu(Base):
    __tablename__ = 'jikgu'
    id = Column(String(120), primary_key=True)
    year = Column(INT, unique=False, nullable=False)
    subject = Column(String(255), unique=False, nullable=False)
    purchase = Column(INT, unique=False, nullable=False)
    percentage = Column(INT, unique=False, nullable=False)

class JPData(Base):
    __tablename__ = 'jpimage'
    subject = Column(String(40), primary_key=True)
    image = Column(LargeBinary)

class JPDictData(Base):
    __tablename__ = 'jpDtwData'
    subject = Column(String(40), primary_key=True)
    data = Column(FLOAT)