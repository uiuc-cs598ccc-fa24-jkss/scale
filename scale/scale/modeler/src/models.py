from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd
import numpy as np
from tabulate import tabulate
from collections import deque, defaultdict
from datetime import datetime

import logging
from opentelemetry.proto.trace.v1.trace_pb2 import TracesData
from google.protobuf.json_format import MessageToDict


class Node:
    """
    A class used to represent a Node in a tree structure.

    Attributes
    ----------
    id : any, optional
        The identifier for the node (default is None)
    children : list
        A list to store the children nodes of the current node

    Methods
    -------
    add_child(child)
        Adds a child node to the current node's children list.
    get_children()
        Returns the list of children nodes.
    """
    def __init__(self, id=None):
        self.id = id 
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def get_children(self):
        return self.children

        logging.debug(f"Node created: {self.id}")

class Span(Node):
    """
    Span class represents a span node with various attributes.

    For reference, the Span data structure is as follows:
    trace_id: str
    span_id: str
    parent_span_id: str or None
    name: str
    kind: str
    start_time_unix_nano: int
    end_time_unix_nano: int
    attributes: List[Dict]
    status: Dict
    flags: int
    service_name: str
    scope_name: str
    scope_version: str

    attributes is a list of dictionaries that, when converted to a dataframe, can be flattened into separate columns.
    This is the basic structure of the dataframe created with the to_df method.
    trace_id | span_id | parent_span_id | name| kind | start_time_unix_nano | end_time_unix_nano | attributes | status | flags | service_name | scope_name  | scope_version |

    Attributes:
        parent_span_id (str or None): The ID of the parent span. Defaults to None if not provided.
        span_id (str): The unique identifier for the span. Must be provided in the data dictionary.
    Methods:
        __init__(self, **data):
            Initializes a Span instance with the provided data dictionary.
            Raises a ValueError if 'span_id' is not provided in the data dictionary.
        __repr__(self):
            Returns a string representation of the Span instance, including all attributes.
        __str__(self):
            Returns a human-readable string representation of the Span instance, including all attributes.
        from_dict(cls, data):
            Class method to create a Span instance from a dictionary.
        to_dict(self):
            Converts the Span instance to a dictionary.
        extract_from_dict(self, data: Dict={}, keys: List=[]):
            Extracts values from the provided dictionary for the specified keys.
        to_df(self, flatten=False):
            Convert the Span instance to a Pandas DataFrame.
    """
    def __init__(self, **data):
        # Initialize all data from the dictionary
        super().__init__()

        self.__dict__.update(data)
        if 'parent_span_id' not in data:
            self.parent_span_id = None
        
        # Get span_id, defaulting to None if not provided
        if not data.get('span_id', None):
            raise ValueError("span_id is required")
        
        self.duration_ms = (int(self.end_time_unix_nano) - int(self.start_time_unix_nano)) / 1e6
        

    def __setattr__(self, name, value):
        # Allow setting all attributes
        super().__setattr__(name, value)

    def __repr__(self):
        # Include all attributes from __dict__ in repr
        attrs = ', '.join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
        return f"Span({attrs})"

    def __str__(self):
        # Include all attributes from __dict__ in str
        attrs = ', '.join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"Span: {attrs}"

    @classmethod
    def from_dict(cls, data):
        """
        Create an instance of the class from a dictionary.

        Args:
            data (dict): A dictionary containing the data to initialize the class instance.

        Returns:
            An instance of the class initialized with the data from the dictionary.
        """
        return cls(**data)

    def to_dict(self):
        """
        Converts the object's attributes to a dictionary.

        Returns:
            dict: A dictionary containing the object's attributes.
        """
        return self.__dict__.copy()

    def extract_from_dict(self, data: Dict={}, keys: List=[]):
        """
        Extracts the value from a dictionary for the first key found in the provided list of keys.
        This may be necessary if keys diverge across different data sources.
        For instance, I've nodticed Tempo uses camelCase for attribute keys, while OpenTelemetry uses snake_case.
        
        Args:
            data (Dict, optional): The dictionary to extract the value from. Defaults to an empty dictionary.
            keys (List, optional): The list of keys to search for in the dictionary. Defaults to an empty list.

        Returns:
            The value associated with the first key found in the dictionary, or None if no keys are found.
        """
        for key in keys:
            if key in data:
                return data[key]

    def to_df(self, flatten=False):
        """
        Converts the Span instance to a DataFrame.

        Args:
            flatten (bool, optional): Whether to flatten the attributes into separate columns. Defaults to False.

        Returns:
            DataFrame: A DataFrame containing the Span instance data.
        """
        def extract_attributes(attributes_list):
            attributes_dict = {}
            for attribute in attributes_list:
                key = attribute['key']
                # Handle different value types (string, int, etc. - probably more types in real data then we have here)
                value = attribute['value'].get('string_value') or attribute['value'].get('int_value', None)
                attributes_dict[key] = value
            return attributes_dict

        df = pd.DataFrame([self.__dict__])

        # drop 'id' and 'children' columns
        df = df.drop(['id', 'children'], axis=1)

        if flatten:
            attributes_df = df['attributes'].apply(extract_attributes).apply(pd.Series)
            df = pd.concat([df.drop('attributes', axis=1), attributes_df], axis=1)

        return df


class Trace:
    """
    A class to represent a Trace consisting of multiple spans.
    Attributes:
    -----------
    trace_id : str
        The unique identifier for the trace.
    spans : Dict[str, Span]
        A dictionary of spans associated with the trace, where the key is the span ID. 
    root_span : str (span_id)
        The root span of the trace, determined by the _build method.
    Methods:
    --------
    __init__(trace_id, spans: List[Span]):
        Initializes the Trace object with a trace_id and a list of spans.
    _build(spans: List[Span]) -> Span:
        Constructs the span tree and identifies the root span.
    to_df(flatten=False):
        Converts the spans to a pandas DataFrame.
    show_tree(root: Span = None, level=0):
        Prints the span tree starting from the root span.
    show_table(flatten=False):
        Converts the trace to a DataFrame and prints it in a tabular format.
    __repr__():
        Returns a string representation of the Trace object.
    __str__():
        Returns a human-readable string representation of the Trace object.
    """
    def __init__(self, trace_id=None, spans: List[Span] = []):
        """
        Initializes the model with a trace ID and a list of spans.

        Args:
            trace_id (str): The unique identifier for the trace.
            spans (List[Span]): A list of Span objects associated with the trace.

        Attributes:
            trace_id (str): The unique identifier for the trace.
            spans (List[Span]): A list of Span objects associated with the trace.
            root_span (Span): The root span built from the list of spans.
        """
        self.span_dict = {span.span_id: span for span in spans}
        self.root_span: str = self._build()
        self.trace_id = trace_id if trace_id else self.root_span.trace_id 
        duration_ms = sum(span.duration_ms for span in self.span_dict.values())
        self.__setattr__('duration_ms', duration_ms)


    @property
    def root_span(self):
        return self.span_dict.get(self._root_span)

    @root_span.setter
    def root_span(self, value):
        self._root_span = value

    def _build(self,) -> Span:
        """
        Constructs a tree of spans from a list of spans.

        This method takes a list of spans and organizes them into a tree structure
        based on their parent-child relationships. Each span is expected to have a 
        unique `span_id` and an optional `parent_span_id`. The span with no 
        `parent_span_id` is considered the root span.

        Args:
            spans (List[Span]): A list of Span objects to be organized into a tree.

        Returns:
            Span: The root span of the constructed tree.

        Raises:
            ValueError: If no root span is found (i.e., no span with `parent_span_id=None`).

        Logs:
            - A warning if multiple root spans are found.
            - An error if a parent span is not found for a given span.
            - A warning if no root span is found, indicating the trace will be dropped.
        """
        root = None

        for span_id, span in self.span_dict.items():
            # Check if the span has a parent span
            if not span.parent_span_id:
                # Check if the root span is already set
                if root is None:
                    root = span_id
                else: 
                    logging.warning(f"Multiple root spans found: {span_id} and {root}")
            else:  
                if span.parent_span_id in self.span_dict:
                    self.span_dict[span.parent_span_id].add_child(span_id)
                else:
                    logging.error(f"Parent span with ID {span.parent_span_id} not found for span {span_id}")

        if root is None:
            # maybe we can use something like in memeory cache to store incomplete traces
            # but for now, we will just raise an exception and drop the trace
            logging.warning("No root span found, dropping trace...")
            raise ValueError("The trace has no root span (no span with parent_span_id=None)")

        return root

    def get_span(self, span_id: str) -> Span:
        """
        Returns the span object for the given span ID.

        Args:
            span_id (str): The ID of the span to retrieve.

        Returns:
            Span: The span object corresponding to the given span ID.
        """
        return self.span_dict.get(span_id, None)

    def to_df(self, flatten=False):
        """
        Converts the spans to a pandas DataFrame.

        Args:
            flatten (bool, optional): If True, flattens the DataFrame. Defaults to False.

        Returns:
            pd.DataFrame: A DataFrame containing the concatenated spans.
        """
        return pd.concat([span.to_df(flatten) for span in self.span_dict.values()], ignore_index=True)

    @staticmethod
    def parse_spans(trace: TracesData) -> list[Span]:
            """
            Parses the spans from the given trace data and returns a list of Span objects.

            Args:
                trace (TracesData): The trace data to parse.

            Returns:
                list[Span]: A list of Span objects extracted from the trace data.
            """
            attr_keys = ('string_value', 'int_value', 'double_value', 'bool_value')

            spans = []

            for resource_span in trace.resource_spans:
                # comprehension to extract resource attributes
                # transform attribute keys to snake_case where attribute key is a dot-separated string
                resource_attributes = {attr.key.replace('.', '_'): getattr(attr.value, key) 
                                        for attr in resource_span.resource.attributes 
                                        for key in attr_keys 
                                        if attr.value.HasField(key)}

                for scope_span in resource_span.scope_spans:
                    scope = scope_span.scope
                    scope_name = scope.name
                    scope_version = scope.version

                    for span in scope_span.spans:

                        # Convert span protobuf message to a dictionary
                        span_dict = MessageToDict(span, preserving_proto_field_name=True)
                        
                        # Add resource-level attributes to the span data (e.g., service.name)
                        span_dict.update(resource_attributes)
                        
                        # Add scope name and version
                        span_dict['scope_name'] = scope_name
                        span_dict['scope_version'] = scope_version

                        spans.append(Span.from_dict(span_dict))         
                    
            return spans

    @classmethod
    def from_proto(cls, trace_data: TracesData):
        return cls(spans=Trace.parse_spans(trace_data))


    def show_tree(self, root: Span = None, level=0):
        """
        Recursively prints the tree structure starting from the given root span.

        Args:
            root (Span, optional): The root span to start printing from. If None, 
                                   the method will start from the instance's root_span.
            level (int, optional): The current level in the tree, used for indentation. 
                                   Defaults to 0.

        Returns:
            None

        Logs:
            - Error if the root span is None.
            - Info for each span printed with indentation based on the level.
            - Error if an exception occurs during the tree printing process.
        """
        try: 
            if root is None:
                root = self.span_dict[self.root_span]  # Start from the root of the tree if not provided

            if root is None:  # make sure we have a root span
                logging.error("Root span is None, cannot print tree")
                return

            logging.info(f"{'    ' * level}Span: [{root.span_id}]")

            for child in root.get_children() or []:
                self.show_tree(self.span_dict[child], level + 1)
        except Exception as e:
            logging.error(f"{e}")
            logging.error(f'root: {root}')

    def show_table(self, flatten=False):
        """
        Converts the trace to a DataFrame and prints it in a tabular format.
        Args:
            flatten (bool, optional): If True, flattens the data frame before printing. Defaults to False.
        Returns:
            None
        """
        try: 
            df = self.to_df(flatten=flatten)
            logging.info(tabulate(df, headers='keys', tablefmt='pretty'))        
        except Exception as e:
            logging.error(f"{e}")
    def __repr__(self):
        return f"Trace({self.trace_id}, {self.span_dict})"

    def __str__(self):
        return f"Trace: {self.trace_id}, {self.span_dict}"


class LatencyTracker:
    """
    A class to track latency data for services and operations.

    There are two main parts to the data:
    The service_data dictionary contains is a dictionary of service names, 
    each with a dictionary of operations and a queue of its most recent calculated latencies.

    The operations dictionary is similar to the service_data dictionary, 
    but it contains a queue of latencies_data for each operation. 
    
    The latency_data is a dictionary containing the latency and start time of the operation.
    """
    def __init__(
            self, 
            queue_length=25
    ):  
        """
        Initialize the latency tracker
        """
        self.service_data = defaultdict(lambda : {
            'latency_data': deque(maxlen=queue_length),
            'total_duration': 0.0,
            'count': 0,
            'operations': defaultdict(lambda: {
                'latency_data': deque(maxlen=queue_length),
                'total_duration': 0.0,
                'count': 0,
            })
        })

    def add_service_latency(
            self, 
            service_name, 
            latency,
    ):
        """
        Add a latency to the tracker
        """
        # add current timestamp to the latency data
        latency_data = {
            'latency': latency,
            'start_time': datetime.now().timestamp(),
        }

        self.service_data[service_name]['latency_data'].append(latency_data)
        self.service_data[service_name]['total_duration'] += latency
        self.service_data[service_name]['count'] += 1

    def add_operation_latency(
            self, 
            service_name, 
            operation_name, 
            start_time,
            latency,
    ):
        """
        Add a latency to the tracker
        """
        latency_data = {
            'latency': latency,
            'start_time': start_time,
        }

        service_info = self.service_data[service_name]
        operation_info = service_info['operations'][operation_name]

        # Add the new latency data
        operation_info['latency_data'].append(latency_data)

        # Update the running totals
        operation_info['total_duration'] += latency
        operation_info['count'] += 1


    def track(
            self, 
            trace: Trace,
    ) -> None:
        """
        Track the latencies of a trace
        Extracts the necessary information from the trace and adds it to the tracker
        """
        service_durations = defaultdict(float)

        for span in trace.span_dict.values():
            self.add_operation_latency(span.service_name, span.name, span.start_time_unix_nano, span.duration_ms)
            service_durations[span.service_name] += span.duration_ms

        for service_name, duration in service_durations.items():
            self.add_service_latency(service_name, duration)

    def get_service_latencies(
            self, 
            service_name,
    ) -> List[float]:
        """
        Get the most recent latencies for a service
        """
        return list(self.service_data[service_name]['latency_data'])

    def get_latency_data(
            self, 
            service_name, 
            operation_name: str=None
    ) -> List[Dict]:
        """
        Get the latency queue data for a specific operation of a service, or for the service itself
        """
        if operation_name:
            return list(self.service_data[service_name]['operations'][operation_name]['latency_data'])
        return list(self.service_data[service_name]['latency_data'])

    def get_latencies(
            self, 
            service_name: str,
            operation_name: str=None,
    ) -> List[float]:
        """
        Method to get the latencies for a service or operation
        """
        latency_data = self.get_latency_data(service_name, operation_name)
        # latency data is a list of {latency, start_time}
        # here we want just the lsit of latencies
        return [attr['latency'] for attr in latency_data]

    def get_service_names(self) -> List[str]:
        """
        Get the names of the services that have been tracked
        """
        return list(self.service_data.keys())

    def get_operation_names(
            self,
            service_name: str
    ) -> List[str]:
        """
        Get the names of the operations for a service
        """
        return list(self.service_data[service_name]['operations'].keys())

    def get_count(
            self,
            service_name: str,
            operation_name: str=None,
    ) -> int:
        """
        Get the count of latencies for a service or operation
        """
        if operation_name:
            return self.service_data[service_name]['operations'][operation_name]['count']
        return self.service_data[service_name]['count']

    def get_total_duration(
            self,
            service_name: str,
            operation_name: str=None,
    ) -> float:
        """
        Get the total duration of latencies for a service or operation
        """
        if operation_name:
            return self.service_data[service_name]['operations'][operation_name]['total_duration']
        return self.service_data[service_name]['total_duration']


    def queue_length(
            self, 
            service_name: str, 
            operation: str=None, 
    ) -> int:
        """
        Get the length of the latency queue for a service or operation 
        """
        if operation:
            return len(self.service_data[service_name]['operations'][operation]['latency_data'])
        return len(self.service_data[service_name]['latency_data'])

class LatencyAnalyzer:
    """
    Perform analysis on latency data to calculate trends and averages of latencies for services and operations.
    """
    def __init__(
            self, 
            latency_tracker: LatencyTracker
    ):
        """
        Initialize the latency analyzer with a latency tracker
        """
        self.latency_tracker = latency_tracker

    def average_latency(
            self, 
            service_name,
            operation_name: str=None
    ) -> float:
        """
        Calculate the average latency for a service
        """
        latencies = self.latency_tracker.get_latencies(service_name=service_name, operation_name=operation_name)
        if not latencies:
            return None
        return np.mean([latency for latency in latencies])

    def p75_latency(
            self,
            service_name: str,
            operation_name: str=None
    ) -> float:
        """
        Calculate the 75th percentile (p75) latency for a service or operation.
        
        Args:
            service_name (str): The name of the service.
            operation_name (str, optional): The name of the operation. If None, calculates for the entire service.
        
        Returns:
            float: The p75 latency for the specified service or operation.
        """
        latencies = self.latency_tracker.get_latencies(service_name=service_name, operation_name=operation_name)
        if not latencies:
            return None
        return np.percentile(latencies, 75)


    def trend(
        self, 
        service_name: str,
        operation_name: str=None
    ) -> float: 
        """
        Calculate the trend of latencies for a service or operation
        """
        latencies = self.latency_tracker.get_latencies(service_name=service_name, operation_name=operation_name)
        if not latencies:
            return 0.0
        return self._calculate_trend(latencies)

    def trend_cusum(
        self, 
        service_name: str,
        operation_name: str=None
    ) -> float: 
        """
        Calculate the trend of latencies for a service or operation
        """
        latencies = self.latency_tracker.get_latencies(service_name=service_name, operation_name=operation_name)
        if not latencies:
            return 0.0
        return self._calculate_trend_cusum(latencies)
    
    def trend_ema(
        self, 
        service_name: str,
        operation_name: str=None
    ) -> float: 
        """
        Calculate the trend of latencies for a service or operation
        """
        latencies = self.latency_tracker.get_latencies(service_name=service_name, operation_name=operation_name)
        if not latencies:
            return 0.0
        return self._calculate_trend_ema(latencies)    

    def operation_average_latencies(
            self, 
            service_name
    ) -> Dict[str, float]:
        """
        Calculate the average latencies for each operation of a service
        """
        operations = self.latency_tracker.service_data[service_name]['operations']
        return {operation_name: self.average_latency(service_name, operation_name) for operation_name in operations}

    def operation_p75_latencies(
            self, 
            service_name
    ) -> Dict[str, float]:
        """
        Calculate the 75th percentile (p75) latencies for each operation of a service.
        
        Args:
            service_name (str): The name of the service.
        
        Returns:
            Dict[str, float]: A dictionary with operation names as keys and their p75 latencies as values.
        """
        operations = self.latency_tracker.service_data[service_name]['operations']
        return {operation_name: self.p75_latency(service_name, operation_name) for operation_name in operations}


    def operation_trends(
            self, 
            service_name
    ) -> Dict[str, float]:
        """
        Calculate the trends of latencies for each operation of a service

        The trend is calculated as the slope of the linear regression line for the latencies.
        """
        operations = self.latency_tracker.service_data[service_name]['operations']
        return {operation_name: self.trend(service_name, operation_name) for operation_name in operations}
    
    def operation_trends_cusum(
            self, 
            service_name
    ) -> Dict[str, float]:
        """
        Calculate the trends of latencies for each operation of a service

        The trend is calculated as the slope of the linear regression line for the latencies.
        """
        operations = self.latency_tracker.service_data[service_name]['operations']
        return {operation_name: self.trend_cusum(service_name, operation_name) for operation_name in operations}
    
    def operation_trends_ema(
            self, 
            service_name
    ) -> Dict[str, float]:
        """
        Calculate the trends of latencies for each operation of a service

        The trend is calculated as the slope of the linear regression line for the latencies.
        """
        operations = self.latency_tracker.service_data[service_name]['operations']
        return {operation_name: self.trend_ema(service_name, operation_name) for operation_name in operations}        
    
    def average_total_latency(
            self, 
            service_name: str, 
            operation_name: str=None
    ) -> float:
        """
        Calculate the average total latency for a service or operation
        """
        if operation_name: 
            return self.latency_tracker.get_total_duration(service_name, operation_name) / self.latency_tracker.get_count(service_name, operation_name)
        return self.latency_tracker.get_total_duration(service_name) / self.latency_tracker.get_count(service_name)    
        

    def _calculate_trend(
            self, 
            latencies
    ) -> float:
        """
        Calculate the trend of latencies using linear regression
        """
        if len(latencies) < 2:
            return None

        x = np.arange(len(latencies))  # for time points (1, 2, 3, ...)
        y = np.array(latencies)

        coeffs = np.polyfit(x, y, 1) 
        trend = coeffs[0]  # get the slope

        return trend
    
    def _calculate_trend_cusum(
            self, 
            latencies, 
            threshold=0
    ) -> float:
        """
        Calculate the cumulative sum of deviations from a target mean or previous trend.
        """
        mean_latency = np.mean(latencies)
        cusum = np.cumsum(np.array(latencies) - mean_latency)
        
        if abs(cusum[-1]) > threshold:
            return cusum[-1] / len(latencies)  # Average shift
        
        return 0  # No significant trend shift detected
    
    def _calculate_trend_ema(
        self,
        latencies, 
        span=10
    ) -> float:
        
        if len(latencies) < span:
            return 0
        
        ema = pd.Series(latencies).ewm(span=span, adjust=False).mean()
        trend = ema.iloc[-1] - ema.iloc[-span]  # difference over the span
        return trend