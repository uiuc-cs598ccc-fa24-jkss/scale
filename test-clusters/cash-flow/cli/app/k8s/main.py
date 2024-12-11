import click
import os

from .. import utils
from . import commands, config

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, '..', "..", "..")

@click.group()
def k8s():
    """Manage Kubernetes clusters."""
    os.chdir(PROJECT_DIR)
    pass

# Command for managing Kubernetes clusters
@k8s.command()
@click.option('--config', '-c', default=None, help='the configuration to apply.')
def start(config):
    """Manage Kubernetes clusters."""
    click.echo("Managing Kubernetes clusters by applying or deleting configurations.")
    utils.run(f"""
        source k8s/venv/bin/activate && \
        ./k8s_manage.sh start {config if config else ''} && \
        deactivate
    """)    

@k8s.command()
# @click.option('--config', '-c', default=None, help='the configuration to delete.')
def stop():
    """Stop the Kubernetes cluster."""
    click.echo("Stopping the Kubernetes cluster.")
    utils.run("""
        source k8s/venv/bin/activate && \
        ./k8s_manage.sh stop && \
        deactivate
    """)    

# @k8s.command()
# @click.option('--service', '-s', default=None, help='The service to get logs for.')
# def logs(service):
#     """Get logs for a service."""
#     click.echo(f"Getting logs for the {service} service.")
#     utils.run(f"./test_scripts/log.sh {service}")

@k8s.command()
@click.argument('service')
def podname(service):
    """Get the pod name for a service."""
    name = commands.get_pod_name(service)
    print(name)

@k8s.command()
@click.argument('service')
def logs(service):
    """Get logs for a service."""
    commands.get_service_logs(service) 

@k8s.command()
def cluster_ip():
    """Get the IP address of the cluster."""
    ip = commands.get_cluster_ip()
    print(ip)

@k8s.command()
@click.argument('service')
def service_ip(service):
    """Get the IP address of a service."""
    ip = commands.get_service_ip(service)
    print(ip)