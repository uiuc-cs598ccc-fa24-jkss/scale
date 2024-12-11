from typing import Iterable
from opentelemetry.proto.trace.v1.trace_pb2 import ResourceSpans


TRACE_DF_COLUMNS = [
    "TraceID",
    "SpanID",
    "ParentID",
    "ServiceName",
    "OperationName",
    "StartTimeUnixNano",
    "Duration",
]


def extract_service(resource_spans: ResourceSpans):
    for attribute in resource_spans.resource.attributes:
        if attribute.key == "service.name":
            return attribute.value.string_value
    return "unknown_service"


def extract_spans(resource_spans_it: Iterable[ResourceSpans]):
    """
    Extract spans for ResourceSpans
    """
    for resource_spans in resource_spans_it:
        service = extract_service(resource_spans)
        for scope_span in resource_spans.scope_spans:
            for span in scope_span.spans:
                yield [
                    str(bytes.hex(span.trace_id)),
                    str(bytes.hex(span.span_id)),
                    (
                        str(bytes.hex(span.parent_span_id))
                        if span.parent_span_id
                        else "root"
                    ),
                    service,
                    span.name,
                    span.start_time_unix_nano,
                    1e-6 * (span.end_time_unix_nano - span.start_time_unix_nano),
                ]
