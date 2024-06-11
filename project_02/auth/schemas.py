import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str

    class Config:
        from_attributes = True


class User(UserBase):
    id: int
    date_created: datetime.datetime

    class Config:
        from_attributes = True


class AddressBase(BaseModel):
    street: str
    landmark: str
    city: str
    country: str
    pincode: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True


class GenerateUserToken(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True


class GenerateOtp(BaseModel):
    email: str


class VerifyOtp(BaseModel):
    email: str
    otp: int
