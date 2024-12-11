from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class OrchestrationClient(ABC):
    """Abstract base class for orchestration backends."""

    @abstractmethod
    def scale_service(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """Scale up a service by increasing the number of replicas."""
        pass

    @abstractmethod
    def get_current_scale(self, *args, **kwargs) -> Optional[int]:
        """Retrieve the current number of replicas for a service."""
        pass

    @abstractmethod
    def get_desired_scale(self, *args, **kwargs) -> Optional[int]:
        """Retrieve the desired number of replicas for a service."""
        pass

    @abstractmethod
    def get_deployments(self, *args, **kwargs) -> Optional[List]:
        """Retrieve the deployments for a service."""
        pass

    @abstractmethod
    def get_scale_max(self, *args, **kwargs) -> Optional[int]:
        """Retrieve the maximum scale for a service."""
        pass
    
    @abstractmethod
    def get_scale_min(self, *args, **kwargs) -> Optional[int]:
        """Retrieve the minimum scale for a service."""
        pass