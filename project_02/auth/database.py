from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
postgres_host = os.environ.get("POSTGRES_HOST")
postgres_db = os.environ.get("POSTGRES_DB")
postgres_user = os.environ.get("POSTGRES_USER")
postgres_password = os.environ.get("POSTGRES_PASSWORD")
postgres_port = os.environ.get("POSTGRES_PORT")


# Assuming your PostgreSQL server is running locally with a database named 'mydatabase'
DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()