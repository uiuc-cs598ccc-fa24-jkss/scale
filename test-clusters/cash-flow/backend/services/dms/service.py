from fastapi import HTTPException
from typing import List
from sqlalchemy.orm import Session

import models
from database import SessionLocal

from server.models.transaction_base import TransactionBase
from server.models.user import User
from server.models.user_create import UserCreate

from server.apis.default_api_base import BaseDefaultApi
from server.models.transaction_create import TransactionCreate

from app_logging import AppLogger, config

logger = AppLogger('DataService')

class DataService(BaseDefaultApi):
    async def add_transactions(
        self,
        transaction: List[TransactionCreate],
    ) -> List[TransactionBase]:
        logger.debug(f'Adding transactions: {transaction}')
        db: Session = SessionLocal()
        try:
            # convert incoming Transaction to models.Transaction
            # TODO need to fix this to use the same type
            transactions = [] 
            for trans in transaction:
                transactions.append(models.Transaction(
                    id=trans.id,
                    account_id=trans.account_id,
                    amount=trans.amount,
                    category=trans.category,
                    description=trans.description,
                    date=trans.date)
                )

            db.add_all(transactions)
            db.commit()
            logger.debug(f'Transactions added: {transactions}')
            return transaction
        except Exception as e:
            logger.error(f'Error adding transactions: {e}')
            db.rollback()
            raise e
        finally:
            db.close()


    async def create_transaction(
        self,
        transaction_create: TransactionCreate,
    ) -> int:
        logger.debug(f'Creating transaction: {transaction_create}')
        db: Session = SessionLocal()
        try:
            db_transaction = models.Transaction(
                account_id=int(transaction_create.account_id),
                amount=transaction_create.amount,
                category=transaction_create.category,
                description=transaction_create.description,
                date=transaction_create.date
                )
            db.add(db_transaction)
            db.commit()
            db.refresh(db_transaction)

            logger.debug(f'db transaction id: {db_transaction.id}')
            return db_transaction.id

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
        

    async def create_user(
        self,
        user_create: UserCreate,
    ) -> User:
        logger.debug(f'Creating user: {user_create}')
        db: Session = SessionLocal()
        
        try:
            db_user = models.User(
                username=user_create.username,
                email=user_create.email,
                hashed_password=user_create.password
                # is_active=True
            )
            db.add(db_user)
            db.commit()
            return db.query(models.User).filter(models.User.username == user_create.username).first()
        except Exception as e:
            logger.error(f'Error creating user: {e}')
            db.rollback()
            raise e
        finally:
            db.close()


    async def get_transaction(
        self,
        transaction_id: int,
    ) -> TransactionBase:
        logger.debug(f'Getting transaction with id: {transaction_id}')


    async def get_transactions(
            self,
            user_id: int,
            skip: int,
            limit: int,
        ) -> List[TransactionBase]:
            """
            Retrieve a list of transactions from the database.

            Args:
                skip (int): The number of transactions to skip.
                limit (int): The maximum number of transactions to retrieve.

            Returns:
                List[TransactionBase]: A list of TransactionBase objects representing the retrieved transactions.
                NOTE: This is returning a [TransactionBase] object, not a [Transaction] object.  This means
                elements returned will not have an id or account_id field.  There is currently an issue with the 
                openapi client generator failing to produce the correct Transaction object. 
            """
            logger.debug(f'Getting transactions for user_id {user_id} with skip: {skip} and limit: {limit}')
            db: Session = SessionLocal()
            try:
                transactions = db.query(models.Transaction).filter(models.Transaction.account_id == str(user_id)).offset(skip).limit(limit).all()
                logger.debug(f'Returning transactions: {transactions}')
                return [
                    TransactionBase(amount=transaction.amount, 
                                    category=transaction.category,
                                    description=transaction.description,
                                    date=transaction.date
                                    ) for transaction in transactions]

            except Exception as e:
                logger.error(f'Error getting transactions: {e}')
                db.rollback()
                raise e
            finally:
                db.close()
        


    async def get_user_by_email(
        self,
        email: str,
    ) -> User:
        logger.debug(f'Getting user with email: {email}')
        db: Session = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.email == email).first()
            return user
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()


    async def get_user_by_username(
        self,
        username: str,
    ) -> User:
        logger.debug(f'Getting user with username: {username}')

        db: Session = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.username == username).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            logger.debug(f'Returning User: {user}')
            return user
        except Exception as e:
            logger.error (f'Error: {e}')
            db.rollback()
            raise e
        finally:
            db.close()