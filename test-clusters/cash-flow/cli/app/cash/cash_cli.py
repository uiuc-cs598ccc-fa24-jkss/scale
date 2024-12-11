import click
import subprocess
import os
import sys
from faker import Faker
from datetime import datetime
from .. import utils
import json
from concurrent.futures import ThreadPoolExecutor

from app import env


# Get the directory where this Python script resides
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, '..', "..", "..")

def add_paths():
    sys.path.insert(0, PROJECT_DIR)

    venv_path = os.path.join(PROJECT_DIR, '.cli', 'lib', 'python3.12', 'site-packages')
    sys.path.insert(0, venv_path)
    venv_path = os.path.join(PROJECT_DIR, '.backend', 'lib', 'python3.12', 'site-packages')
    sys.path.insert(0, venv_path)

    app_dir = os.path.join(PROJECT_DIR, 'cli', 'app')
    add_to_sys_path(app_dir)

    # Add the backend to the path
    backend_dir = os.path.join(PROJECT_DIR, 'backend')
    services_dir = os.path.join(backend_dir, 'services')
    interface_dir = os.path.join(backend_dir, 'interfaces')
    add_to_sys_path(backend_dir)
    add_to_sys_path(services_dir)
    add_to_sys_path(interface_dir)

@click.group()
def cash():
    """Main entry point for CLI."""
    add_paths()
    pass

@cash.group()
def build():
    """Build Docker containers and publish to Docker Hub."""
    pass

@build.command()
def templates():
    """Generates Kubernetes configuration files from templates."""
    utils.run("""
        source k8s/venv/bin/activate && \
        python k8s/build.py && \
        deactivate
    """)

@build.command()
@click.option('--service', '-s', default=None, help='The service to generate OpenAPI clients for.')
def containers(service):
    """Build Docker containers and publish to Docker Hub."""
    click.echo("Building Docker containers and publishing to Docker Hub.")
    os.chdir(PROJECT_DIR)
    utils.run(f"./build.sh {service}")
    
@cash.group()
def openapi():
    """Generate OpenAPI client and server APIs for a service."""
    pass

@openapi.command()
def clean():
    """Clean up the generated OpenAPI client and server APIs."""
    click.echo("Cleaning up the generated OpenAPI client and server APIs.")
    utils.run("./deploy.sh clean")

@openapi.command()
def generate():
    """Generate the OpenAPI client and server APIs for all services."""
    click.echo("Generating the OpenAPI client and server APIs for all services.")
    utils.run("./deploy.sh deploy")

def add_to_sys_path(root_dir):
    """Recursively add directories to sys.path, excluding virtual environments and cache directories."""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip unnecessary directories
        if "venv" in dirnames:
            dirnames.remove("venv")  # Do not descend into 'venv'
        if "__pycache__" in dirnames:
            dirnames.remove("__pycache__")  # Skip __pycache__ directories
        if "pip" in dirpath or "_vendor" in dirpath:
            continue  # Skip pip or vendorized paths
            
        sys.path.insert(0, dirpath)

            
@cash.command()
@click.option('--environment', '-e', default='docker', help='The environment the system is running on. Used for cli tool configuration.')
def test(environment):
    """Run the CLI tool."""
    from cli.app.test import main as test_main  
    env.setup_api(environment)
    test_main.main()


# Command for deploying APIs
@cash.command()
@click.option('--action', '-a', default='deploy', help='The service to generate OpenAPI clients for.')
def deploy(action):
    """Generate OpenAPI client and server APIs for a service."""
    if action in ['clean', 'deploy']:
        if action == 'clean':
            click.echo("Cleaning up the generated OpenAPI client and server APIs.")
        elif action == 'deploy':
            click.echo("Generating the OpenAPI client and server APIs for all services.")
        os.chdir(PROJECT_DIR)
        utils.run(f'./deploy.sh {action}')


@cash.command()
@click.option('--users', '-u', type=click.INT, default=10, show_default=True, help='The number of users to simulate.')
@click.option('--threads', '-t', type=click.INT, default=3, show_default=True, help='The number of threads.')
@click.option('--transactions', '-x', type=click.INT, default=3, show_default=True, help='The number of transactions to generate.')
@click.option('--environment', '-e', default='kube', help='The environment the system is running on. Used for cli tool configuration.')
def sim(users, threads, transactions, environment):
    """Simulate user activity.
    This command simulates user activity by registering users, logging in, and creating transactions.
    """
    os.chdir(PROJECT_DIR)
    from app.test import registration
    from app.test.sim import create_users, create_user_file, login_user
    import app.test.sim as sim 

    if not os.getenv('CLUSTER_ENV', False): 
        env.setup_api(environment)

    sim_users = sim.create_users(users)
    user_file = sim.create_user_file(sim_users)

    # Register each user
    def register_user(user, user_data):
        registration.send_registration_request(user_data['email'])
        code = registration.get_registration_code(user_data['email'])
        print(f"Code for {user_data['email']}: {code}")
        if code:
            if registration.verify_code(user_data['email'], code):
                print(f"Verified {user_data['email']}")
                data = {
                    "username": user,
                    "email": user_data['email'],
                    "password": user_data['password']
                }
                sim.send_registration_request(data)

    # login and transaction process for each user
    def login_and_create_transaction(user, user_data):
        token = sim.login_user(user, user_data['password'])
        for i in range(transactions):
            if i % 2 == 0:
                sim.create_fake_transaction(token)
            else:
                print ("Viewing transactions")
                response = sim.get_transactions(token)
                print (response.json())

    # handle registration in parallel
    with ThreadPoolExecutor(max_workers=threads) as executor:
        # Submit registration tasks
        for user in sim_users:
            executor.submit(register_user, user, sim_users[user])

    # handle login and transactions in parallel
    with ThreadPoolExecutor(max_workers=threads) as executor:
        # Submit login and transaction tasks
        for user in sim_users:
            executor.submit(login_and_create_transaction, user, sim_users[user])


if __name__ == '__main__':
    cash()
