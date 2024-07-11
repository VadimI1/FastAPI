from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Mem(Base):
    __tablename__ = 'mem'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    photo = Column(LargeBinary)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    email = Column(String)
    password = Column(String)
