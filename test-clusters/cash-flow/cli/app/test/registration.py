from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich.panel import Panel
import requests
import os
from app.test import auth
import registration_client 
import redis
import time


# Rich Console for displaying output
console = Console()

# Function to get the API URL, can be dynamically set at runtime
def get_registration_url():
    return f"{os.getenv('REGISTRATION_API_URL', 'http://localhost:8084')}/api/v1/registration"

# Lazy initialization of the cache, only initialized when called
_cache = None

# Lazy initialization of the client, only initialized when called
_registration_api = None


def get_cache():
    """
    Lazily initialize and return redis cache.
    """
    global _cache

    if _cache is None:
        try:
            if  os.getenv("CLUSTER_ENV", False):
                _cache = redis.from_url(os.getenv("REDIS_URL"))
            else:
                (host, port) = os.environ.get("REDIS_URL").split('/')[-1].split(':')
                print("REDIS_HOST", host)
                _cache = redis.Redis(host=host, port=port, db=0)
        except Exception as e:
            print(f"Error: {e}")
            _cache = None
    return _cache


def get_registration_client():
    """
    Lazily initialize and return the RegistrationApi client.
    """
    global _registration_api

    if _registration_api is None:
        # Initialize configuration with dynamically set URL
        config = registration_client.Configuration()
        config.host = get_registration_url()

        # Initialize the API client with the config
        api_client = registration_client.ApiClient(config)

        # Create the RegistrationApi client
        _registration_api = registration_client.RegistrationApi(api_client)

    return _registration_api


def prompt_for_verify():
    """
    Prompt the user for verification confirmation, with options for manual and auto verification.
    """
    option = Prompt.ask("Verify code? (y = manual, a = auto)", choices=["y", "a"], default="y")
    
    if option == "y":
        print("Manual verification selected.")
        return True  # Proceed with manual verification
    elif option == "a":
        print("Auto-verification selected. Bypassing manual verification.")
        return False  # Bypass manual verification


def send_registration_request(email: str):
    """
    Send a registration request to the registration API.

    Args:
        email (str): The email address of the user to register.

    Returns:
        None
    """
    request = registration_client.RegistrationRequest(email=email)

    try:
        # Use the lazily initialized registration client
        registration_api = get_registration_client()

        # Call the API to register the user
        response = registration_api.register_user(request)
        return response
    except Exception as e:
        print(f'Error: {e}')
        return

def register():
    """
    Register a user by prompting for their email and sending a registration request.
    """
    email = Prompt.ask("Enter your email")

    send_registration_request(email=email)
    request = registration_client.RegistrationRequest(email=email)

    if prompt_for_verify():
        verify_registration(email=email)
    else:
        auto_verify_registration(email=email)

def get_registration_code(email: str, retries=3):
    """
    Get the code from the cache using the email as the key.

    Args:
        email (str): The email address of the user.

    Returns:
        str: The code stored in the cache.
    """
    cache = get_cache()
    code = None
    while not cache.exists(email) and retries > 0:
        print (f"email {email} not found in cache, waiting for 1 second")
        time.sleep(1)
        retries -= 1
    if cache.exists(email):
        code = cache.get(email)
        if code and isinstance(code, bytes):
            code = code.decode('utf-8')
    return code

def verify_code(email: str, code: str):
    """
    Verify the code by comparing it with the code stored in the cache.

    Args:
        email (str): The email address of the user.
        code (str): The code entered by the user.

    Returns:
        bool: True if the code is verified, False otherwise.
    """
    request = registration_client.CodeVerificationRequest(email=email, code=code)
    try: 
        registration_api = get_registration_client()
        verified = registration_api.verify_registration(request)
        print(f'Verification response: {verified}')
        return verified
    except Exception as e:
        print (f'Error: {e}')
        return False


def auto_verify_registration(email: str=None):
    """
    Automatically verifies the registration by sending a code verification request to the registration API.

    Returns:
        None
    """
    code = get_registration_code(email)
    request = registration_client.CodeVerificationRequest(email=email, code=code)
    if verify_code(email, code):
        auth.register(email=email)


def verify_registration(email: str=None):
    """
    Verifies the registration by prompting the user to enter their email and code,
    and then sends a code verification request to the registration API.

    Returns:
        None
    """
    if not email:
        email = Prompt.ask("Enter your email")

    code = Prompt.ask("Enter the code")
    request = registration_client.CodeVerificationRequest(email=email, code=code)

    try: 
        registration_api = get_registration_client()
        verified = registration_api.verify_registration(request)
        print(f'Verification response: {verified}')
        if verified:
            console.print("Registration verified", style="bold green")
            auth.register(email=email)
    except Exception as e:
        print (f'Error: {e}')
        return