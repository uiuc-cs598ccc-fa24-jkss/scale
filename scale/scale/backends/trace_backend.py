from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime

class TraceBackend(ABC):
    """Abstract base class for trace backends."""

    @abstractmethod
    def get_trace_by_id(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a trace by its ID."""
        pass

    @abstractmethod
    def search_traces(
        self,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search for traces within a time range."""
        pass