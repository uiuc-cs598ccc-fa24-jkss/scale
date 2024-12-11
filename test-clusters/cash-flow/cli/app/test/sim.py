from app.test import registration, auth, transactions
from faker import Faker
from datetime import datetime
import json

# List of categories for transactions
categories = [
    'Groceries', 'Entertainment', 'Utilities', 'Healthcare', 
    'Restaurants', 'Travel', 'Shopping', 'Rent', 
    'Education', 'Insurance', 'Subscriptions', 'Gym Membership', 
    'Fuel', 'Public Transport', 'Clothing', 'Electronics', 
    'Home Improvement', 'Loans', 'Savings', 'Gifts', 
    'Charity', 'Childcare', 'Pets', 'Car Maintenance', 
    'Investment', 'Taxes', 'Vacation', 'Legal Fees', 
    'Household Supplies', 'Phone Bill', 'Internet Bill'
]

def send_registration_request(data: dict):
    """
    Sends a registration request to the auth API.
    """
    response = auth.send_registration_request(data)
    return response

def create_user_file(data: dict) -> str:
    """
    Creates a JSON file with the simulated user data.
    """
    timestamp = datetime.now().strftime(f"%Y-%m-%d_%H%M%S")
    user_file = f'./sim_users_{timestamp}.json'
    print (f'Creating user file: {user_file}')
    with open(user_file, 'w') as f:
        f.write(json.dumps(data, indent=4))
    return user_file


def create_users(num_users: int) -> dict:
    """
    Creates simulated user data.
    """
    fake = Faker()
    sim_users = {}

    for _ in range(num_users):
        sim_users.update({
                fake.user_name(): {
                    'email': fake.email(),
                    'password': fake.password(),
                }
        })
    return sim_users

def login_user(username: str, password: str):
    """
    Logs in a user and returns the access token.
    """
    token = auth.send_login_request(username, password)
    return token


def create_fake_transaction_data():
    """
    Creates simulated transaction data.
    """
    fake = Faker()
    amount = fake.random_int(min=1, max=1000)
    category = fake.random_element(categories)
    description = fake.sentence()
    _date = fake.date_time_this_year(before_now=True, after_now=False, tzinfo=None).isoformat()

    data = {
        "amount": amount,
        "category": category,
        "description": description,
        "date": _date
    }
    return data


def create_fake_transaction(token: str):
    """
    Creates a fake transaction.
    """
    data = create_fake_transaction_data()
    response = transactions.create_transaction(token, data)
    return response    

    
def get_transactions(token: str):
    """
    Retrieves transactions for a user.
    """
    response = transactions.get_transactions(token)
    return response