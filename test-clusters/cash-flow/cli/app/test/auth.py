from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich.panel import Panel
import requests
from dotenv import dotenv_values
import os


console = Console()

def get_auth_url():
    return f"{os.getenv(f'AUTH_API_URL', default='http://localhost:8083')}/api/v1/auth"


def prompt_for_username() -> str:
    username = Prompt.ask("Enter your username")
    return username

def prompt_for_email() -> str:
    email = Prompt.ask("Enter your email")
    return email

def prompt_for_password() -> str:
    password = Prompt.ask("Enter your password", password=True)
    return password


def send_login_request(username: str, password: str):
    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "read write",
        "client_id": "your_client_id",
        "client_secret": "your_client_secret"
    }
    response = requests.post(f'{get_auth_url()}/token', data=data)

    if response.status_code == 200:
        success_message = Text("Login Successful", style="bold green")
        console.print(Panel(success_message, title="Success", expand=False))
        response = response.json()
        return response["access_token"]
    else:
        failure_message = Text(f"{response.status_code} - {response.content}", style="bold red")
        console.print(Panel(failure_message, title="Login Failed", expand=False))
    return None


def login():
    username = Prompt.ask("Enter your username")
    password = Prompt.ask("Enter your password", password=True)

    return send_login_request(username, password)


def send_registration_request(data:dict):
    response = requests.post(f'{get_auth_url()}/register', json=data)

    if response.status_code == 200:
        success_message = Text("User created successfully", style="bold green")
        console.print(Panel(success_message, title="Success", expand=False))
    else:
        failure_message = Text(f"{response.status_code} - {response.content}", style="bold red")
        console.print(Panel(failure_message, title="Failed", expand=False))


def register(email: str=None):
    username = Prompt.ask("Enter your username")
    if not email:
        email = Prompt.ask("Enter your email")
    password = Prompt.ask("Enter your password", password=True)

    data = {
        "username": username,
        "email": email,
        "password": password
    }

    send_registration_request(data)