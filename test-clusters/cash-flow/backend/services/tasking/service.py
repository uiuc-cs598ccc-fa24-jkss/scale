from server.apis.default_api_base import BaseDefaultApi

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from server.models.process_bulk_transactions200_response import ProcessBulkTransactions200Response
from server.models.process_bulk_transactions_request import ProcessBulkTransactionsRequest
from server.models.process_enrollment200_response import ProcessEnrollment200Response
from server.models.process_enrollment_request import ProcessEnrollmentRequest
from server.models.process_transaction200_response import ProcessTransaction200Response
from server.models.process_transaction_request import ProcessTransactionRequest
from server.models.send_registration_code_email200_response import SendRegistrationCodeEmail200Response
from server.models.send_registration_code_email_request import SendRegistrationCodeEmailRequest
from server.models.send_welcome_email200_response import SendWelcomeEmail200Response
from server.models.send_welcome_email_request import SendWelcomeEmailRequest

import tasks

from app_logging import AppLogger, config
logger = AppLogger('TaskingService')

class TaskingService(BaseDefaultApi):
    
    async def process_bulk_transactions(
        self,
        process_bulk_transactions_request: ProcessBulkTransactionsRequest
    ) -> ProcessBulkTransactions200Response:
        # create a transaction
        logger.debug(f'process_bulk_transactions_request: {process_bulk_transactions_request}')
        logger.debug(f'Queuing bulk transactions for processing')
        tasks.process_bulk_transactions.delay(process_bulk_transactions_request.model_dump())
        return ProcessBulkTransactions200Response(
            status="success",
            message="Transactions processed"
        ) 

    async def process_enrollment(
        self,
        process_enrollment_request: ProcessEnrollmentRequest,
    ) -> ProcessEnrollment200Response:
        return ProcessEnrollment200Response(
            status="success",
            message="Enrollment processed - not implemented"
        )

    async def process_transaction(
        self,
        process_transaction_request: ProcessTransactionRequest,
    ) -> ProcessTransaction200Response:
        logger.debug (f'Queuing transaction request: {process_transaction_request}')
        tasks.process_transaction.delay(process_transaction_request.model_dump())

        return {'status': 'success', 'message': 'Transaction processed'}    

    async def send_registration_code_email(
        self,
        request: SendRegistrationCodeEmailRequest,
    ) -> SendRegistrationCodeEmail200Response:
        logger.debug(f'Sending registration code {request.code} email to {request.email}')
        tasks.send_registration_code_email.delay(request.email, request.code)
        return SendRegistrationCodeEmail200Response(
            status="success",
            message=f"Registration code email sent to {request.email}"
        )

    async def send_welcome_email(
        self,
        send_welcome_email_request: SendWelcomeEmailRequest,
    ) -> SendWelcomeEmail200Response:
        logger.debug(f'Sending welcome email to {send_welcome_email_request.user_email}')
        tasks.send_welcome_email.delay(send_welcome_email_request.user_email)
        return SendWelcomeEmail200Response(
            status="success",
            message="Welcome email sent"
        )

    async def health_check_api_health_get(self) -> object:
        return {"status": "Healthy"}