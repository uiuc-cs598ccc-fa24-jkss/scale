import logging
from collections import defaultdict
import os
from typing import Dict, List
from google.protobuf.json_format import MessageToDict #, MessageToJson

from opentelemetry.proto.collector.trace.v1 import trace_service_pb2_grpc
from opentelemetry.proto.collector.trace.v1 import trace_service_pb2

from models import Span, Trace


def log_request(request):
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        # Detailed logging (DEBUG level): Log the entire message
        request_dict = MessageToDict(request, preserving_proto_field_name=True)
        logging.debug(f"Full Trace request: {request_dict}")
    elif logging.getLogger().isEnabledFor(logging.INFO):
        scope_spans = sum([len(resource_span.scope_spans) for resource_span in request.resource_spans])
        # Basic logging (INFO level): Log only summary information
        logging.info(f"Received Trace data with {len(request.resource_spans)} resource spans and {scope_spans}.")


class TraceService(trace_service_pb2_grpc.TraceServiceServicer):

    TRACE_THRESHOLD = int(os.getenv("OTEL_TRACE_THRESHOLD", 100))

    def __init__(self):
        self.trace_dict = defaultdict(list)
        self.total_traces = 0
        self.traces_dropped = 0

    def add_span(self, span: Span):
        """
        Adds a span to the trace dictionary.

        Args:
            span (Span): The span object to be added. It must have a trace_id attribute.

        Raises:
            KeyError: If the trace_id of the span does not exist in the trace dictionary.
        """
        self.trace_dict[span.trace_id].append(span)

    def _should_process(self):
        """
        Determines whether the trace dictionary has reached the threshold for processing.

        Returns:
            bool: True if the number of traces in the trace dictionary is greater than or equal to the TRACE_THRESHOLD, False otherwise.
        """
        if (len(self.trace_dict) >= TraceService.TRACE_THRESHOLD):
            logging.debug(f"Threshold of {TraceService.TRACE_THRESHOLD} traces reached. Processing...")
            return True

    def process_traces(self):
        """
        Processes the traces stored in the trace dictionary.

        This method iterates over the trace dictionary, creates Trace objects for each trace ID and its associated span list,
        and appends them to a list of traces. If an error occurs during the creation of a Trace object, it logs the error.
        After processing, it logs the number of processed traces and the number of traces dropped, then clears the trace dictionary.

        Returns:
            list: A list of processed Trace objects.
        """
        traces = [] 
        if self._should_process():
            self.total_traces += len(self.trace_dict)
            for trace_id, span_list in self.trace_dict.items():
                try:
                    trace = Trace(trace_id, span_list) 
                    traces.append(trace)
                except Exception as e:
                    logging.error(f"Error creating trace for trace_id {trace_id}: {e}")
                    self.traces_dropped += 1
            logging.info(f"Successfully processed {len(traces)} traces.")
            logging.info(f"Traces dropped in current batch: {len(self.trace_dict) - len(traces)}")
            self.trace_dict.clear() 
        return traces

    def parse_spans(self, request):
        """
        Parses spans from the given request and processes them.
        This method iterates over resource spans, extracts resource attributes,
        and processes each span within the scope spans. It converts each span
        protobuf message to a dictionary, adds resource-level attributes, scope
        name, and version to the span data, and then adds the span to the internal
        storage.
        Args:
            request: The request object containing resource spans to be parsed.
        Returns:
            None
        """
        # Counts the number of spans extracted from the request
        span_count = 0

        # Defines attribute keys to extract from resource attributes
        attr_keys = ('string_value', 'int_value', 'double_value', 'bool_value')

        # Iterate over resource spans
        for resource_span in request.resource_spans:
            # comprehension to extract resource attributes
            # transform attribute keys to snake_case where attribute key is a dot-separated string
            resource_attributes = {attr.key.replace('.', '_'): getattr(attr.value, key) 
                                   for attr in resource_span.resource.attributes 
                                   for key in attr_keys 
                                   if attr.value.HasField(key)}
            

            # Iterate over all scope_spans (or instrumentation_library_spans)
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

                    self.add_span(Span.from_dict(span_dict))
                    span_count += 1

        logging.info(f"Extracted {span_count} spans from request.")
 
    async def Export(self, request, context):
        """
        Handles the export of trace data.

        Args:
            request: The incoming request containing trace data.
            context: The context of the request.

        Returns:
            An instance of ExportTraceServiceResponse indicating the result of the export operation.
        """
        logging.info("Received trace data:")
        log_request(request)
        
        # Parse the spans into Span objects and stores them in the trace dictionary keyed by trace_id
        self.parse_spans(request)

        # This will execute if the the preconditions we set are met (in self._should_process)
        # Right now we are just checking if we've reached a certain threshold
        # Presumably we'll want to pass this to a modeling agent for further processing
        traces = self.process_traces()
        if traces:
            logging.info(f"Generated {len(traces)} traces.")
            for trace in traces:
                trace.show_tree()
                trace.show_table()
        
            logging.info(f"Total traces: {self.total_traces}")
            logging.info(f"Total Traces dropped: {self.traces_dropped}")
            logging.info(f"Dropped percentage: {self.traces_dropped / self.total_traces * 100:.2f}%")

        return trace_service_pb2.ExportTraceServiceResponse()