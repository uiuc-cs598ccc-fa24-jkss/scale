from abc import ABC, abstractmethod
from typing import List, Dict

class ConfigInterface(ABC):

    @abstractmethod
    def update_config(self):
        """Update the configuration file."""
        pass

    @abstractmethod
    def get_latency_threshold(self, resource: str) -> Dict[str, str]:
        """Get latency threshold for a specific resource."""
        pass

    @abstractmethod
    def get_target_deployment(self, resource: str) -> str:
        """Get the target deployment for a specific resource."""
        pass

    @abstractmethod
    def get_all_resources(self) -> List[str]:
        """Get a list of all available resources."""
        pass

    @abstractmethod
    def get_resource_config(self, resource: str) -> Dict[str, any]:
        """Get the full configuration for a specific resource."""
        pass
