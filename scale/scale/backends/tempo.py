import requests
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backends.trace_backend import TraceBackend

logger = logging.getLogger(__name__)

class TempoBackend(TraceBackend):
    def __init__(self, host: str="tempo", port=3200, token: Optional[str] = None):
        """
        Initializes a TempoBackend object.

        Args:
            base_url (str): The base URL of the Tempo API.
            token (Optional[str], optional): The authorization token. Defaults to None.
        """
        self.base_url = f'http://{host}:{port}'
        self.headers = {}
        if token:
            self.headers['Authorization'] = f'Bearer {token}'

    def _call_api(self, method: str, endpoint: str, params: Dict={}, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Calls the Tempo API.

        Args:
            method (str): The HTTP method to use.
            endpoint (str): The API endpoint.
            params (Dict, optional): Query parameters. Defaults to {}.
            **kwargs: Additional keyword arguments to pass to requests.

        Returns:
            Optional[Dict[str, Any]]: The response data as a dictionary, or None if an error occurred.
        """
        url = f'{self.base_url}/{endpoint}'
        try:
            response = requests.request(method, url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.error(f'Tempo HTTP Error: {e.response.status_code} - {e.response.text}')
        except Exception as e:
            logger.exception('An unexpected error occurred while calling the Tempo API.')
        return None

    def get_trace_by_id(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a trace by its ID.

        Args:
            trace_id (str): The ID of the trace.

        Returns:
            Optional[Dict[str, Any]]: The trace data as a dictionary, or None if the trace is not found.
        """
        endpoint = f'api/traces/{trace_id}'
        return self._call_api('GET', endpoint)

    def search_traces(
        self,
        start_time: datetime=None,
        end_time: datetime=None,
        limit: int = 20,
        service_name: Optional[str] = None,
        name: Optional[str] = None,
        **query_args
    ) -> List[Dict[str, Any]]:
        """
        Searches for traces the provided parameters.
        According to the Tempo API documentation all parameters are optional.
        
        Tempo will accept the following query parameters:
        start, end, service.name, name, limit

        The parameters can be specified as keyword arguments, 
        or in the query_args dictionary.  The query_args dictionary
        will take precedence over any keyword arguments.  Leaving it
        this way for now, but we'll probably move to just using the 
        query_args dictionary in the future, as it promotes a more
        generic approach and can be used by the caller without having 
        to know which client is being used.  
        The issue with the using a strict keywords approach is that the service name
        in the arguments is 'service.name' which is not a valid python keyword argument. 
        We can make a decision once we start looking into alternative backend clients.

        Args:
            start_time (datetime, optional): The start time of the search range.
            end_time (datetime, optional): The end time of the search range.
            limit (int, optional): The maximum number of traces to retrieve. Defaults to 100.
            service_name (Optional[str], optional): The name of the service.
            name (Optional[str], optional): The name of the operation

            **query_args: Additional query parameters.

        Returns:
            List[Dict[str, Any]]: A list of trace data as dictionaries.
        """
        query_params = {}
        endpoint = 'api/search'


        # add parameters to the query if they are provided
        if start_time:
            query_params['start'] = int(start_time.timestamp())  # nanoseconds
        if end_time:
            query_params['end'] = int(end_time.timestamp())
        if service_name:
            query_params['service.name'] = service_name
        if name:
            query_params['name'] = name
        query_params['limit'] = limit

        query_params.update(query_args)

        response = self._call_api('GET', endpoint=endpoint, params=query_params)
        return response.get('traces', [])