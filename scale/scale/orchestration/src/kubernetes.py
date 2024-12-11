from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import Any, Dict, List, Optional
import logging

from orchestration.orchestration_client import OrchestrationClient

logger = logging.getLogger(__name__)

class KubernetesClient(OrchestrationClient):
    def __init__(self, namespace: str = "default", config_file: str = None, in_cluster=False):
        """
        Initializes a KubernetesClient object.

        Args:
            namespace (str): The Kubernetes namespace. Defaults to 'default'.
            config_file (str, optional): The path to the kubeconfig file. If None, uses the default kubeconfig.
        """
        print (f"Creating orchestrator for namespace: {namespace}, config_file: {config_file}")
        if config_file:
            config.load_kube_config(config_file=config_file)  # Load from a specific config file

        # Load in-cluster config if running in a pod
        elif in_cluster:
            config.load_incluster_config()

        # load default kubeconfig
        else:
            config.load_kube_config()  # Load from default kubeconfig

        # self.core_v1 = client.CoreV1Api()  # For core resources like pods, configmaps
        self.autoscaling_v1 = client.AutoscalingV1Api()  # For managing HPA
        self.apps_v1 = client.AppsV1Api()  # For managing deployments, statefulsets, etc.
        self.namespace = namespace

        print (f"Orchestrator created for namespace: {namespace}")

    def scale_service(self, deployment: str, replica_diff: int) -> Optional[Dict[str, Any]]:
        """
        Adjusts the number of replicas for a given service by a specified difference.

        Args:
            service_name (str): The name of the service.
            replica_diff (int): The number of replicas to add or subtract. Positive values scale up, negative values scale down.

        Returns:
            Optional[Dict[str, Any]]: The scaling response, or None if an error occurred.
        """
        try:
            current_replicas = self.get_current_scale(deployment)
            if current_replicas is None:
                logger.error(f"Could not retrieve current scale for {deployment}")
                return None

            new_replica_count = max(0, current_replicas + replica_diff)  # Ensure replicas never go below 0
            if new_replica_count == current_replicas:
                logger.info(f"No scaling action required for {deployment}, current replicas: {current_replicas}")
                return None

            body = {"spec": {"replicas": new_replica_count}}
            scale_response = self.apps_v1.patch_namespaced_deployment_scale(
                name=deployment,
                namespace=self.namespace,
                body=body
            )
            logger.info(f"Scaled {deployment} to {new_replica_count} replicas (difference: {replica_diff}).")
            return scale_response.to_dict()
        except ApiException as e:
            logger.error(f"Failed to scale {deployment}: {e}")
            return None

    def _get_scale_info(self, deployment: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the scale information for a service.

        Args:
            service_name (str): The name of the service.

        Returns:
            Optional[Dict[str, Any]]: The scale information, or None if an error occurred.
        """
        try:
            scale_info = self.apps_v1.read_namespaced_deployment_scale(
                name=deployment,
                namespace=self.namespace
            )
            return scale_info.to_dict()
        except ApiException as e:
            logger.error(f"Failed to get scale info for {deployment}: {e}")
            return {}

    def get_current_scale(self, deployment: str) -> Optional[int]:
        """
        Retrieve the current number of replicas for a service.
        
        Args:
            service_name (str): The name of the service.
            
        Returns:
            Optional[int]: The current number of replicas, or None if an error occurred.
        """
        
        scale_info = self._get_scale_info(deployment)
        if not scale_info:
            return None
        status = scale_info.get("status", {})
        if not status:
            return None
        return status.get("replicas", 0)
         
    def get_desired_scale(self, deployment) -> Optional[int]:
        """
        Retrieve the desired number of replicas for a service.

        Args:
            service_name (str): The name of the service.

        Returns:
            Optional[int]: The desired number of replicas, or None if an error occurred.
        """
        scale_info = self._get_scale_info(deployment)
        spec = scale_info.get("spec", {})
        if not spec:
            return None
        return spec.get("replicas")


    def get_deployments(self) -> Optional[List]:
        """
        Retrieve the deployments for a service.

        Args:
            namespace (str): The namespace to search for deployments.

        Returns:
            Optional[List]: A list of deployment objects, or None if an error occurred.
        """
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace=self.namespace)
            return deployments.items
        except ApiException as e:
            logger.error(f"Failed to get deployments for namespace {self.namespace}: {e}")
            return None
       
    def _get_spec_min_max_replicas(self, deployment: str) -> Dict[str, int]:
        """
        Retrieve the minimum and maximum number of replicas for a service.

        Args:
            service_name (str): The name of the service.

        Returns:
            Dict[str, int]: A dictionary containing the minimum and maximum replicas.
        """
        hpa = self.autoscaling_v1.read_namespaced_horizontal_pod_autoscaler(
            name=deployment,
            namespace=self.namespace
        )
        
        if not hpa:
            return {"min_replicas": 1, "max_replicas": 1}
        
        min = hpa.spec.get("min_replicas", 1)
        max = hpa.spec.get("max_replicas", 1)
        
        return {"min_replicas": min, "max_replicas": max} 

        
    def get_scale_max(self, deployment: str) -> Optional[int]:
        """
        Retrieve the maximum scale for a service.

        Args:
            service_name (str): The name of the service.

        Returns:
            Optional[int]: The maximum number of replicas, or None if an error occurred.
        """
        return self._get_spec_min_max_replicas(deployment=deployment).get("max_replicas")

    def get_scale_min(self, deployment: str) -> Optional[int]:
        """
        Retrieve the minimum scale for a service.

        Args:
            service_name (str): The name of the service.

        Returns:
            Optional[int]: The minimum number of replicas, or None if an error occurred.
        """
        return self._get_spec_min_max_replicas(deployment=deployment).get("min_replicas")
    