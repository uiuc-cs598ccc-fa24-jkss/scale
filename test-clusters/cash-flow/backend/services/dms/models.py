from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base

class Transaction(Base):
    """
    Represents a financial transaction.

    Attributes:
        id (int): The unique identifier of the transaction.
        account_id (str): The identifier of the account associated with the transaction.
        amount (float): The amount of the transaction.
        category (str): The category of the transaction.
        description (str): The description of the transaction.
        date (datetime): The date of the transaction.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, index=True)
    amount = Column(Float)
    category = Column(String)
    description = Column(String)
    date = Column(DateTime)
