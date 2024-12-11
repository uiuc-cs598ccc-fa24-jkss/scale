import os
import string
import random
from fastapi import HTTPException
import redis
from server.apis.registration_api_base import BaseRegistrationApi
from server.models.registration_request import RegistrationRequest
from server.models.task_response import TaskResponse
from server.models.code_verification_request import CodeVerificationRequest
from server.models.code_verification_response import CodeVerificationResponse

import interfaces.internal.auth.auth_client as auth_client
import interfaces.internal.tasking.tasking_client as tasking_client
from interfaces.internal.tasking.tasking_client.models import SendRegistrationCodeEmailRequest

from app_logging import AppLogger, config

cache = redis.Redis(host='redis', port=6379, db=0)

logger = AppLogger('RegistrationService')

auth_config = auth_client.Configuration()
auth_config.host = os.getenv('AUTH_API_URL', 'http://localhost:8080')
api_client = auth_client.ApiClient(auth_config)
auth_api = auth_client.AuthApi(api_client)

tasking_config = tasking_client.Configuration()
tasking_config.host = os.getenv('TASKING_API_URL', 'http://localhost:8080')
api_client = tasking_client.ApiClient(tasking_config)
tasking_api = tasking_client.DefaultApi(api_client)

class RegistrationService(BaseRegistrationApi):
    
    async def register_user(self, request: RegistrationRequest) -> TaskResponse:
        """Register a new user.  Args:     user (schemas.UserCreate): The user data to be registered.     db (Session, optional): The database session. Defaults to Depends(get_db).  Returns:     schemas.User: The registered user data.  Raises:     HTTPException: If the username is already registered."""

        validation_response = auth_api.validate_user(email=request.email)
        
        # Check if the email is already registered
        if validation_response.exists:
            raise HTTPException(status_code=400, detail="Email already registered")

        else:
            code = self._generate_registration_code()

            cache.set(request.email, code, ex=600)
            
            code_request = SendRegistrationCodeEmailRequest(email=request.email, code=code)
            tasking_api.send_registration_code_email(code_request)
            return TaskResponse(status='success', message='User registered successfully')

    async def verify_registration(self, request: CodeVerificationRequest) -> TaskResponse:
        """Verify a user registration code.  Args:     email (str): The email address of the user.     code (str): The registration code.  Returns:     schemas.TaskResponse: The response message."""
        logger.debug(f'Verifying registration code for email: {request.email}')
        stored_code = cache.get(request.email)
        if not stored_code:
            raise HTTPException(status_code=400, detail="Code not found or expired")
        if stored_code.decode() == request.code:
            cache.delete(request.email)
            return CodeVerificationResponse(valid=True)
        else:
            raise HTTPException(status_code=400, detail="Invalid code")


    @staticmethod
    def _generate_registration_code(length=6):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))