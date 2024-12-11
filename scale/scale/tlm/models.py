from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd
from tabulate import tabulate
import logging



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
        
        logging.debug(f"Span created: {self.span_id}")

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
    def __init__(self, trace_id, spans: List[Span]):
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
        self.trace_id = trace_id
        self.span_dict = {span.span_id: span for span in spans}
        self.root_span: Span = self._build()

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
