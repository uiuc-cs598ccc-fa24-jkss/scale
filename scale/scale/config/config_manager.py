import os
from typing import Dict, List, Any
from config.config_interface import ConfigInterface
import yaml
import glob
import re

class ConfigManager(ConfigInterface):
    def __init__(self, config_path):
        self.config_path = config_path
        self.config_data = []
        self._load_config()

    def _load_config(self):
        """Load the YAML configuration file."""

        if os.path.exists(self.config_path):
            files = glob.glob(f'{self.config_path}/*.yaml')
            files += glob.glob(f'{self.config_path}/*.yml')
            loaded_configs = []

            for file in files:
                try:
                    with open(file, 'r') as stream:
                        loaded_configs += list(yaml.safe_load_all(stream))
                except yaml.YAMLError as e:
                    print(f"Error loading config file '{file}': {e}")
        
            self.config_data = loaded_configs
        else:
            print(f"Config file '{self.config_path}' not found.")
            self.config_data = [] 

                   
    def get_latency_threshold(self, resource: str) -> Dict[str, str]:
        """Retrieve latency threshold data for the specified resource if it exists in the config file."""
        latency_info = {}
        for config in self.config_data:
            if (
                config.get("kind") == "LatencyBasedAutoScaler" and
                config.get("spec", {}).get("target", {}).get("deploymentName", "") == resource
            ):
                # Extract the latency values and split into value and units
                for bound in ['upperBound', 'lowerBound']:
                    entry = config['spec']['latencyThreshold'].get(bound, 'N/A')
                    match = re.match(r'(\d+)([a-zA-Z]+)', entry)
                    if match:
                        value = int(match.group(1))  # Convert value to integer
                        units = match.group(2)
                        latency_info[bound] = {'value': value, 'units': units}
                    else:
                        latency_info[bound] = {'value': entry, 'units': ''}  # If entry is 'N/A' or not matching pattern
                break
        else:
            print(f"Resource '{resource}' not found in config file.")
        return latency_info
    
    def get_target_deployment(self, resource: str) -> str:
        """Retrieve the deployment name of the specified resource."""
        for config in self.config_data:
            if (config.get("kind") == "LatencyBasedAutoScaler" and
                config.get("spec", {}).get("target", {}).get("deploymentName", "").startswith(resource)):
                return config['spec']['target']['deploymentName']
        print(f"Resource '{resource}' not found in config file.")
        return ""

    def get_all_resources(self) -> List[str]:
        """Return a list of all resource names defined as LatencyBasedAutoScaler in the config file."""
        resource_names = []
        for config in self.config_data:
            if config.get("kind") == "LatencyBasedAutoScaler":
                resource_names.append(config.get("spec", {}).get("target", {}).get("deploymentName", ""))
        return [name for name in resource_names if name]  # Filter out any empty names

    def get_resource_config(self, resource: str) -> Dict[str, any]:
        """Retrieve all configuration information for the specified resource."""
        for config in self.config_data:
            if (config.get("kind") == "LatencyBasedAutoScaler" and
                config.get("spec", {}).get("target", {}).get("deploymentName", "").startswith(resource)):
                return config
        print(f"Resource '{resource}' not found in config file.")
        return {}

    def update_config(self):
        print ("Update triggered")
        self._load_config()

'''
# For testing only:
if __name__ == "__main__":
    config_manager = ConfigManager("config.yaml")
    resource_name = input("Enter the resource name (e.g., auth): ")

    # Retrieve and print latency threshold data of given resource
    latency_data = config_manager.get_latency_threshold(resource_name)
    print(f"\nLatency Threshold Data of '{resource_name}':\n", latency_data)

    # Retrieve and print target deployment data of a given resource
    target_deployment_data = config_manager.get_target_deployment(resource_name)
    print(f"\nTarget Deployment Data of '{resource_name}':\n", target_deployment_data)

    # Get all defined resources in config file
    all_resources = config_manager.get_all_resources()
    print("\nAll defined resources in config file:\n", all_resources)

    # Retrieve and print full resource configuration of given resource
    resource_config = config_manager.get_resource_config(resource_name)
    print(f"\nFull Resource Configuration of '{resource_name}':\n", resource_config)

'''
