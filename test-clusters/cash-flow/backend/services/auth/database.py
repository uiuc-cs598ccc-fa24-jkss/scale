import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# URL-encode the password to safely include it in the connection string
encoded_password = urllib.parse.quote(os.getenv('USER_DB_PASSWORD'))

# Create the database connection URL
# TODO: update the database URL creation to be more dynamic.  Should be configurable if using a different database. 
DATABASE_URL = f"postgresql://{os.getenv('USER_DB_USER')}:{encoded_password}@{os.getenv('USER_DB_HOST')}:{os.getenv('USER_DB_HOST_PORT')}/{os.getenv('USER_DB_DB')}"

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30
)

# Instrument the SQLAlchemy engine
SQLAlchemyInstrumentor().instrument(engine=engine)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for the declarative models
Base = declarative_base()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
