from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
import requests
from datetime import datetime
import os


def get_transaction_url():
    return f"{os.getenv('TRANSACTION_API_URL', 'http://localhost:8082')}/api/v1/transactions"

console = Console()

def get_auth_header(token: str):
    return {
        "Authorization": f"Bearer {token}"  
    }

def get_transaction_data() -> dict:
    amount = Prompt.ask("Enter the amount")
    category = Prompt.ask("Enter the category")
    description = Prompt.ask("Enter the description")
    _date = Prompt.ask("Enter the date", default=datetime.now().isoformat())

    data = {
        "amount": float(amount),
        "category": category,
        "description": description,
        "date": _date
    }
    return data

def send_transaction_request(token: str, data: dict):
    try:
        headers = get_auth_header(token)
        response = requests.post(f'{get_transaction_url()}', json=data, headers=headers)
        return response
    except Exception as e:
        print (f"Error sending transaction request: {e}")
        return None

def create_transaction(token: str, data: dict = {}):
    console.print("Creating transaction...")
    if not data:
        data = get_transaction_data()

    response = send_transaction_request(token=token, data=data)

    if response.status_code == 200:
        success_message = Text("Transaction created successfully", style="bold green")
        console.print(Panel(success_message, title="Success", expand=False))
    else:
        failure_message = Text(f"{response.status_code} - {response.content}", style="bold red")
        console.print(Panel(failure_message, title="Failed", expand=False))

def show_transactions_table(transactions: list):
    table = Table(title="Transactions")
    table.add_column("Amount", style="green")
    table.add_column("Category", style="yellow")
    table.add_column("Description", style="blue")
    table.add_column("Date", style="blue")

    for transaction in transactions:
        table.add_row(
            str(transaction["amount"]),
            str(transaction["category"]),
            str(transaction["description"]),
            str(transaction["date"])
        )

    console.print(table)

def get_transactions(token: str):
    return requests.get(f'{get_transaction_url()}', headers=get_auth_header(token))

def view_transactions(token: str):
    console.print("Viewing transactions...")
    console.print("1. View all transactions")
    console.print("2. View transaction by ID")

    option = Prompt.ask("Enter your choice", choices=["1", "2"])

    if option == "1":
        response = get_transactions(token)
        if response.status_code == 200:
            transactions = response.json()
            show_transactions_table(transactions)
        else:
            failure_message = Text(f"{response.status_code} - {response.content}", style="bold red")
            console.print(Panel(failure_message, title="Failed", expand=False))

def show_transactions_menu(token: str):
    while True:
        console.print("\nSelect transaction type:")
        console.print("1. Create Transaction")
        console.print("2. View Transactions")
        console.print("3. Exit")

        option = Prompt.ask("Enter your choice", choices=["1", "2", "3"])

        if option == "1":
            create_transaction(token)
        elif option == "2":
            view_transactions(token)
        elif option == "3":
            break
