import datetime as _dt
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    ForeignKey
)
from sqlalchemy.orm import relationship
from passlib.hash import bcrypt
from database import Base, engine
from database import Base

Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    is_verified = Column(Boolean, default=False)
    otp = Column(Integer)
    hashed_password = Column(String)
    addresses = relationship("Address", back_populates="user")
    date_created = Column(DateTime, default=_dt.datetime.utcnow)

    def verify_password(self, password: str):
        return bcrypt.verify(password, self.hashed_password)


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, index=True)
    street = Column(String)
    landmark = Column(String)
    city = Column(String)
    country = Column(String)
    pincode = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="addresses")
    latitude = Column(Float)
    longitude = Column(Float)
