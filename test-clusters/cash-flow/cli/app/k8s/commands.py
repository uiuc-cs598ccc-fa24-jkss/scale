from . import command_adapter as adapter

def start(config: str=None):
    """
    Manage Kubernetes clusters by applying or deleting configurations.

    Args:
        config (str): The configuration to apply.
    """
    command = f"""
    source k8s/venv/bin/activate && \
    ./k8s_manage.sh start {config if config else ''} && \
    deactivate
    """
    adapter.run(command)

def get_pod_info(service: str=None) -> dict:
    """
    Get the pod name for all services, or a specific service.

    Args:
        service (str): The service to get the pod name for.

    Returns:
        dict: dictionary with the information from 
        {kubectl get pods -n <namespace>} command.
        if service is None, return all pods.
        otherwise, return the pod name for the service.

        
    """
    command = "kubectl get pods -n cash-flow"

    if service: 
        command += f" | grep {service}"        
    
    result = adapter.run(command, capture_output=True)
    return result.strip()

def get_pod_name(service: str) -> str:
    """
    Get the pod name for a service.

    Args:
        service (str): The service to get the pod name for.

    Returns:
        str: The pod name for the service.
    """
    pod_info = get_pod_info(service=service)
    pod_name = pod_info.split()[0]
    return pod_name

def get_service_logs(service: str):
    """
    Get logs for a service.

    Args:
        service (str): The service to get logs for.
    """
    pod_name = get_pod_name(service)
    get_pod_logs(pod_name)
 
def get_pod_logs(pod_name: str):
    """
    Get logs for a pod.

    Args:
        pod_name (str): The name of the pod to get logs for.
    """
    command = f"""
    kubectl logs {pod_name} -n cash-flow 
    """
    adapter.run(command, live_output=True)

def get_cluster_ip():
    """
    Get the IP address of the cluster.

    Returns:
        str: The IP address of the cluster.
    """
    command = "kubectl get nodes -o wide | grep -v NAME | awk '{print $6}'"
    # or 
    # command = "minikube ip"
    result = adapter.run(command, capture_output=True)
    
    return result.strip()

def get_service_port(service: str, namespace: str="cash-flow"):
    """
    Get the port of a service.

    Args:
        service (str): The service to get the port for.
        namespace (str): The namespace of the service.

    Returns:
        str: The port of the service.
    """
    command = f"""
    kubectl get svc -n {namespace} | grep {service} | awk '{{print $5}}' | awk -F'[:/]' '{{print $2}}'
    """
    result = adapter.run(command, capture_output=True)
    
    return result.strip()

def get_service_ip(service: str):
    """
    Get the IP address of a service.

    Args:
        service (str): The service to get the IP address for.

    Returns:
        str: The IP address of the service.
    """
    cluster_ip = get_cluster_ip().strip()
    service_port = get_service_port(service).strip()
    result = f"http://{cluster_ip}:{service_port}" 
    print (f"Service IP {service}: {result}")
    return result