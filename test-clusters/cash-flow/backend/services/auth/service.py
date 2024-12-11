import os

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, Security, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from datetime import datetime, timedelta

from server.apis.auth_api_base import BaseAuthApi
from server.models.token import Token
from server.models.user import User
from server.models.user_create import UserCreate
from server.models.extra_models import TokenModel
from server.models.validation_response import ValidationResponse
from server.models.token_authorization_response import TokenAuthorizationResponse
import server.security_api as security_api
import security
import crud

import interfaces.internal.tasking.tasking_client as tasking_client
from interfaces.internal.tasking.tasking_client.models import SendWelcomeEmailRequest

from app_logging import AppLogger, config

logger = AppLogger('AuthService')

# TODO: inject the configuration
tasking_config = tasking_client.Configuration()
tasking_config.host = os.getenv('TASKING_API_URL', 'http://localhost:8080')
api_client = tasking_client.ApiClient(tasking_config)
tasking_api = tasking_client.DefaultApi(api_client)

# OAuth2PasswordBearer tells FastAPI to expect a token in the "Authorization" header using the "Bearer" scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes={})

# Password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService(BaseAuthApi):
       
    async def get_api_auth_me(
        self,
        token: str,
    ) -> User:
        """Retrieve the currently authenticated user.  Parameters: - current_user: The currently authenticated user.  Returns: - The current user as a response model."""
        token_model = security_api.get_token_model(token)
        username = token_model.sub
        return crud.get_user_by_username(username)

    async def post_api_auth_register(
        self,
        user_create: UserCreate,
    ) -> User:
        """Register a new user.  Args:     user (schemas.UserCreate): The user data to be registered.     db (Session, optional): The database session. Defaults to Depends(get_db).  Returns:     schemas.User: The registered user data.  Raises:     HTTPException: If the username is already registered."""
        user_create.password = security.get_password_hash(user_create.password)
        user = crud.create_user(user=user_create)
        response = tasking_api.send_welcome_email(
            SendWelcomeEmailRequest(user_email=user.email)
        )
        
        return user

    async def post_api_auth_token(
        self,
        grant_type: str,
        username: str,
        password: str,
        scope: str,
        client_id: str,
        client_secret: str,
    ) -> Token:
        """Logs in a user and returns an access token.  Parameters: - db (Session): The database session. - form_data (OAuth2PasswordRequestForm): The form data containing the username and password.  Returns: - dict: A dictionary containing the access token and token type."""

        JWT_EXPIRATION = int(os.getenv('JWT_EXPIRATION', 30))

        logger.debug(f'username: {username}, password: {password}, grant_type: {grant_type}, scope: {scope}, client_id: {client_id}, client_secret: {client_secret}') 

        logger.debug ("validating user")
        user = security.authenticate_user(username, password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug ("generating token")
        access_token_expires = timedelta(minutes=JWT_EXPIRATION)
        # access_token_expires = timedelta(minutes=int(os.getenv('JWT_EXPIRATION', 30))) 
        access_token = self.create_access_token(
            data={"sub": username, "id": user.id}, expires_delta=access_token_expires)

        return {"access_token": access_token, "token_type": "bearer"}

    async def authorize_token(self, token: TokenModel) -> User:
        """
        Authorize the token and retrieve the current user.
        """

        logger.debug(f'token: {token}')
        return TokenAuthorizationResponse(id=int(token.id)) 

    async def validate_user(self, id: int = None, username: str = None, email: str = None) -> ValidationResponse:
        # Ensure at least one field is provided
        if not any([id, username, email]):
            raise HTTPException(
                status_code=400,
                detail="At least one of 'id', 'username', or 'email' must be provided."
            )
        
        # Prepare the parameters using dictionary comprehension
        params = {k: v for k, v in {"id": id, "username": username, "email": email}.items() if v is not None}
        logger.debug(f'params: {params}')   
        
        user_exists = await self.query_user_in_database(**params)
        
        # Return the response
        return ValidationResponse(exists=user_exists)

    async def query_user_in_database(self, **user_info) -> bool:
        # Perform the query based on the first available parameter
        if 'id' in user_info:
            logger.debug(f'querying user by id: {user_info["id"]}')
            user = crud.get_user_by_id(user_info['id'])
        elif 'username' in user_info:
            logger.debug(f'querying user by username: {user_info["username"]}')
            user = crud.get_user_by_username(user_info['username'])
        elif 'email' in user_info:
            logger.debug(f'querying user by email: {user_info["email"]}')
            user = crud.get_user_by_email(user_info['email'])
        
        logger.debug(f'user: {user}') 
        return user is not None
         

    # @staticmethod
    def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        """
        Retrieve the current user based on the provided JWT token.
        """
        logger.debug(f'token: {token}')

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        JWT_KEY = str(os.getenv('JWT_KEY',))
        JWT_ALGORITHM = str(os.getenv('JWT_ALGORITHM', 'HS256'))

        try:
            payload = jwt.decode(token, JWT_KEY, algorithms=[JWT_ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = AuthService.get_user(username)
        if user is None:
            raise credentials_exception

        logger.debug(f"returning user: {user}")
        return user

    # @staticmethod
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a new JWT token with the provided data and expiration time.
        """

        JWT_SECRET_KEY = str(os.getenv('JWT_SECRET_KEY',))
        JWT_ALGORITHM = str(os.getenv('JWT_ALGORITHM', 'HS256'))

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        print (f'to_encode: {to_encode}')
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
        return encoded_jwt