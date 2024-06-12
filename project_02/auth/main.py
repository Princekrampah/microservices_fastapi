from typing import List
from fastapi import HTTPException
from fastapi import FastAPI, Depends, status
import schemas
from sqlalchemy.orm import Session
import models
import service as services
import logging
import database
import pika

# rabbitmq connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost"))
channel = connection.channel()
channel.queue_declare(queue='email_notification')


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
logging.basicConfig(level=logging.INFO)
models.Base.metadata.create_all(models.engine)


@app.post("/api/users",  tags=['User Auth'])
async def create_user(
        user: schemas.UserCreate,
        db: Session = Depends(services.get_db)):
    db_user = await services.get_user_by_email(email=user.email, db=db)

    if db_user:
        logging.info('User with that email already exists')
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="User with that email already exists")

    user = await services.create_user(user=user, db=db)

    # TODO: add response model
    return {
        "msg": "User Registered, Please verify email to activate account !",
        "user_data": user,
        "status": status.HTTP_200_OK
    }


# Endpoint to check if the API is live
@app.get("/check_api")
async def check_api():
    return {
        "msg": "Connected to API Successfully",
        "status": status.HTTP_200_OK
    }


@app.post("/api/token", tags=['User Auth'])
async def generate_token(
    # form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
    user_data: schemas.GenerateUserToken,
        db: Session = Depends(services.get_db)):
    user = await services.authenticate_user(email=user_data.username, password=user_data.password, db=db)

    if user == "is_verified_false":
        logging.info(
            'Email verification is pending. Please verify your email to proceed. ')
        raise HTTPException(
            status_code=403, detail="Email verification is pending. Please verify your email to proceed.")

    if not user:
        logging.info('Invalid Credentials')
        raise HTTPException(
            status_code=401, detail="Invalid Credentials")

    logging.info('JWT Token Generated')
    generated_token = await services.create_token(user=user)

    return {
        "token": generated_token
    }


@app.get("/api/users/me", response_model=schemas.User, tags=['User Auth'])
async def get_user(user: schemas.User = Depends(services.get_current_user)):
    return {
        "user_details": user
    }


@app.get("/api/users/profile", tags=['User Auth'])
async def get_user(email: str, db: Session = Depends(services.get_db)):
    user = db.query(models.User and models.Address).filter_by(id=1).first()

    return {
        "user_details": user
    }


@app.post("/api/users/generate_otp", response_model=str, tags=["User Auth"])
async def send_otp_mail(userdata: schemas.GenerateOtp, db: Session = Depends(services.get_db)):
    user = await services.get_user_by_email(email=userdata.email, db=db)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="User is already verified")

    # Generate and send OTP
    otp = services.generate_otp()
    print(otp)

    services.send_otp(userdata.email, otp, channel)

    # Store the OTP in the database
    user.otp = otp
    db.add(user)
    db.commit()

    return "OTP sent to your email"


@app.post("/api/users/verify_otp", tags=["User Auth"])
async def verify_otp(user_data: schemas.VerifyOtp, db: Session = Depends(services.get_db)):
    user = await services.get_user_by_email(email=user_data.email, db=db)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.otp or user.otp != user_data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Update user's is_verified field
    user.is_verified = True
    user.otp = None  # Clear the OTP
    db.add(user)
    db.commit()

    return {
        "msg": "Email verified successfully"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
