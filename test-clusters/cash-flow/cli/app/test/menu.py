from rich.console import Console
from rich.prompt import Prompt
from auth import login
from transactions import show_transactions_menu
from registration import register

console = Console()

def show_api_menu(token: str):
    while True:
        console.print("\nAPI to test:")
        console.print("1. Auth")
        console.print("2. Transactions")
        console.print("3. Data Management")
        console.print("4. Tasking")
        console.print("5. Logout")

        option = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"])

        if option == "1":
            print("Testing Auth API")
        elif option == "2":
            print("Testing Transactions API")
            show_transactions_menu(token)
        elif option == "3":
            print("Testing Data Management API")
        elif option == "4":
            print("Testing Tasking API")
        elif option == "5":
            console.print("Logging out...", style="bold red")
            break

def show_login_menu():
    while True:
        console.print("\nPlease choose an option:")
        console.print("1. Login")
        console.print("2. Register")
        console.print("3. Exit")

        option = Prompt.ask("Enter your choice", choices=["1", "2", "3"])

        if option == "1":
            access_token = login()
            if access_token:
                show_api_menu(token=access_token)
        elif option == "2":
            register()
        elif option == "3":
            break
