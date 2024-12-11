from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database

from server.main import app as generated_app

from database import Base, engine
from service import DataService
from health import HealthService

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")

    # Check if the database exists
    print (f"Checking if database {engine.url.database} exists.")
    try:
        if not database_exists(engine.url):
            print (f"Database {engine.url.database} does not exist.")
            create_database(engine.url)
            print(f"Database {engine.url.database} created.")
        
            # Create tables if they do not exist
        else: 
            print(f"Database {engine.url.database} exists.")

        Base.metadata.create_all(bind=engine)
        yield
    except Exception as e:
        print(f"Error creating database: {e}")

app = FastAPI(lifespan=lifespan)

app.mount("/internal/v1/data", generated_app)
