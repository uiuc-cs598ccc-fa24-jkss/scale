from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base

class User(Base):
    """
    Represents a user.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        hashed_password (str): The hashed password of the user.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
