from sqlalchemy.orm import Session
import models
from server.models.user_create import UserCreate 
from fastapi import Depends
from database import get_db
import security



def get_user_by_username(username: str) -> models.User:
    db: Session = next(get_db())
    try:
        user = db.query(models.User).filter(models.User.username == username).first()
        return user
    finally:
        db.close()

def get_user_by_email(email: str) -> models.User:
    db: Session = next(get_db())
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        return user
    finally:
        print ('Closing db')
        db.close()

def get_user_by_id(user_id: int) -> models.User:
    db: Session = next(get_db())

    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        return user
    finally:
        db.close()

def create_user(user: UserCreate) -> models.User:
    db: Session = next(get_db())
    try: 
        hashed_password = security.get_password_hash(user.password)
        db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.close()
        return db_user
    except Exception as e:
        db.rollback()
        print(f'Error creating user: {e}')
        raise e
    finally:
        print('Closing db') 
        db.close()

