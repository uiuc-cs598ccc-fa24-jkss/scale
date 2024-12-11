import os
from fastapi import Depends, Security  # noqa: F401

from server.apis.transactions_api_base import BaseTransactionsApi

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

# from server.models.transaction import Transaction
from server.models.transaction_base import TransactionBase
from server.models.task_response import TaskResponse
from server.security_api import get_token_OAuth2PasswordBearer
from server.models.extra_models import TokenModel

import interfaces.internal.tasking.tasking_client as tasking_client
import interfaces.internal.dms.dms_client as dms_client
import interfaces.internal.auth.auth_client as auth_client
from interfaces.internal.auth.auth_client import TokenAuthorizationResponse

from interfaces.internal.tasking.tasking_client import ProcessBulkTransactionsRequest, ProcessTransactionRequest

from app_logging import AppLogger, config

logger = AppLogger('TransactionService')

# TODO: inject the configuration
tasking_config = tasking_client.Configuration()
tasking_config.host = os.getenv('TASKING_API_URL', 'http://localhost:8080')
api_client = tasking_client.ApiClient(tasking_config)
tasking_api = tasking_client.DefaultApi(api_client)

dms_config = dms_client.Configuration()
dms_config.host = os.getenv('DMS_API_URL', 'http://localhost:8080')
api_client = dms_client.ApiClient(dms_config)
dms_api = dms_client.DefaultApi(api_client)

auth_config = auth_client.Configuration()
auth_config.host = os.getenv('AUTH_API_URL', 'http://localhost:8080')
api_client = auth_client.ApiClient(auth_config)
auth_api = auth_client.AuthApi(api_client)

class TransactionService(BaseTransactionsApi):

    async def delete_api_transaction_id(
        self,
        transaction_id: int,
    ) -> TransactionBase:
        """Delete a transaction by its ID. Requires a valid JWT token."""
        logger.debug(f'Deleting transaction with ID: {transaction_id}') 
        logger.warning("Method delete_api_transaction_id not implemented")

        logger.debug("Returning dummy transaction")
        return TransactionBase(
            # id=transaction_id,
            # account_id=1,
            amount=100,
            category="food",
            description="some description",
            date="2021-01-01"
        )


    async def get_api_transactions(
        self,
        token: TokenAuthorizationResponse,
        skip: int,
        limit: int,
    ) -> List[TransactionBase]:
        """Retrieve a list of transactions. Requires a valid JWT token."""
        logger.debug(f'Getting transactions with skip: {skip} and limit: {limit}') 
        # user = self.get_user_by_username(token.id)

        transactions = dms_api.get_transactions(user_id=int(token.id), skip=skip, limit=limit)
        
        logger.debug(f'Transactions: {transactions}') 
        
        return transactions  
       
    async def get_api_transactions_id(
        self,
        transaction_id: int,
    ) -> TransactionBase:
        """Retrieve a transaction by its ID. Requires a valid JWT token."""
        logger.debug(f'Getting transaction with ID: {transaction_id}') 
        logger.warning("Method get_api_transactions_id not implemented")
        
        #TODO: Implement this method

        logger.debug("Returning dummy transaction")
        return TransactionBase(
            # id=transaction_id,
            # account_id=1,
            amount=100,
            category="food",
            description="some description",
            date="2021-01-01"
        )

    async def post_api_transaction_create(
        self,
        token: TokenAuthorizationResponse,
        transaction_base: TransactionBase
    ) -> TaskResponse:
        """Create a new transaction. This triggers a background task. Requires a valid JWT token."""
        logger.debug(f'Creating transaction: {transaction_base}')

        # user = self.get_user_by_username(token.sub)


        logger.debug (f'token: {token}')

        transaction = transaction_base.model_dump()
        transaction['account_id'] = int(token.id)
        
        # logger.info(f'Creating transaction for user: {transaction}')

        try: 
            response = tasking_api.process_transaction({'transaction': transaction})
            logger.debug(f'Transaction created successfully: {response}')
            return TaskResponse(status="success", message="Transaction created successfully")
        except Exception as e:
            logger.debug(f'Error processing transaction: {e}')
            return TaskResponse(status="failed", message=str(e))

    async def post_api_transactions_bulk(
        self,
        token: TokenModel,
        transaction_create: List[tasking_client.TransactionCreate],
    ) -> TaskResponse:
        """Add multiple transactions at once. Requires a valid JWT token."""
        logger.debug("Adding bulk transactions")
        logger.debug(f'Transaction: {transaction_create}')

        # Ensure that the security token is available
        # if not token:
        #     raise HTTPException(status_code=403, detail="Invalid or missing JWT token")

        # Convert the list of transactions to a bulk request
        request = ProcessBulkTransactionsRequest.from_dict({'transactions_data': transaction_create})

        try:
            # Call the background task for processing transactions
            response = await tasking_api.process_bulk_transactions(request)

            # Assuming the response has a status and transactions_data field
            return TaskResponse(status="success", transactions_data=response.transactions_data)
        except Exception as e:
            logger.debug(f'TransactionService: Error processing bulk transactions: {e}')
            return TaskResponse(status="failed", message=str(e))

    
    def get_user_by_username(self, username: str) -> Dict:
        """Retrieve a user by their username."""
        logger.debug(f'Getting user with username: {username}') 
        return dms_api.get_user_by_username(username)