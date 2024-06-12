import jwt
from sqlalchemy.orm import Session
from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
from database import Base, SessionLocal, engine
import schemas
import models
import random
import json
import pika
import time
import os

# Load environment variables
JWT_SECRET = os.getenv("JWT_SECRET")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
oauth2schema = OAuth2PasswordBearer("/api/token")


def create_database():
    # Create database tables
    return Base.metadata.create_all(bind=engine)


def get_db():
    # Dependency to get a database session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_email(email: str, db: Session):
    # Retrieve a user by email from the database
    # and _models.User.is_verified == True
    return db.query(models.User).filter(models.User.email == email).first()


async def create_user(user: schemas.UserCreate, db: Session):
    # Create a new user in the database
    try:
        valid = validate_email(user.email)
        name = user.name
        email = valid.email
    except EmailNotValidError:
        raise HTTPException(
            status_code=404, detail="Please enter a valid email")

    user_obj = models.User(email=email, name=name,
                            hashed_password=bcrypt.hash(user.password))
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    
    return user_obj


async def authenticate_user(email: str, password: str, db: Session):
    # Authenticate a user
    user = await get_user_by_email(email=email, db=db)

    if not user:
        return False

    if not user.is_verified:
        return 'is_verified_false'

    if not user.verify_password(password):
        return False

    return user


async def create_token(user: models.User):
    # Create a JWT token for authentication
    user_obj = schemas.User.model_validate(user)
    user_dict = user_obj.model_dump()
    del user_dict["date_created"]
    token = jwt.encode(user_dict, JWT_SECRET, algorithm="HS256")
    return dict(access_token=token, token_type="bearer")


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2schema)):
    # Get the current authenticated user from the JWT token
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(models.User).get(payload["id"])
    except:
        raise HTTPException(
            status_code=401, detail="Invalid Email or Password")
    return schemas.User.model_validate(user)


def generate_otp():
    # Generate a random OTP
    return str(random.randint(100000, 999999))


def connect_to_rabbitmq():
    # Connect to RabbitMQ
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(RABBITMQ_URL))
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("Failed to connect to RabbitMQ. Retrying in 5 seconds...")
            time.sleep(5)


def send_otp(email, otp, channel):
    # Send an OTP email notification using RabbitMQ
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    message = {'email': email,
               'subject': 'Account Verification OTP Notification',
               'other': 'null',
               'body': f'Your OTP for account verification is: {otp} \n Please enter this OTP on the verification page to complete your account setup. \n If you did not request this OTP, please ignore this message.\n Thank you '
               }

    try:
        queue_declare_ok = channel.queue_declare(
            queue='email_notification', passive=True)
        current_durable = queue_declare_ok.method.queue

        if current_durable:
            if queue_declare_ok.method.queue != current_durable:
                channel.queue_delete(queue='email_notification')
                channel.queue_declare(queue='email_notification', durable=True)
        else:
            channel.queue_declare(queue='email_notification', durable=True)

        channel.basic_publish(
            exchange="",
            routing_key='email_notification',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        print("Sent OTP email notification")
    except Exception as err:
        print(f"Failed to publish message: {err}")
    finally:
        channel.close()
        connection.close()
