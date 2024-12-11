import asyncio
import csv
import grpc
from opentelemetry.proto.collector.trace.v1 import (
    trace_service_pb2,
    trace_service_pb2_grpc,
)
from opentelemetry.proto.trace.v1.trace_pb2 import ResourceSpans, ScopeSpans, TracesData


class TraceAssembler(trace_service_pb2_grpc.TraceServiceServicer):

    def __init__(self, csv_path, count):
        self.csv_file = open(csv_path, "w")
        self.csv_writer = csv.writer(self.csv_file)
        self.trace_ids = set()
        self.trace_count = count
        self.count_reached_event = asyncio.Event()
        self.csv_writer.writerow(
            [
                "TraceID",
                "SpanID",
                "ParentID",
                "OperationName",
                "StartTimeUnixNano",
                "Duration",
            ]
        )

    async def wait_count(self):
        await self.count_reached_event.wait()

    def close(self):
        self.csv_file.flush()
        self.csv_file.close()

    async def Export(
        self, request: trace_service_pb2.ExportTraceServiceRequest, context
    ):
        for resource_span in request.resource_spans:
            for scope_span in resource_span.scope_spans:
                for span in scope_span.spans:
                    trace_id = bytes.hex(span.trace_id)[-16:]
                    span_id = bytes.hex(span.span_id)
                    parent_span_id = bytes.hex(span.parent_span_id) or "root"
                    start_time = span.start_time_unix_nano
                    duration = int(1e-6 * (span.end_time_unix_nano - start_time))
                    operation_name = span.name
                    self.trace_ids.add(trace_id)
                    if len(self.trace_ids) > self.trace_count:
                        self.count_reached_event.set() 
                    else:
                        self.csv_writer.writerow(
                            [
                                trace_id,
                                span_id,
                                parent_span_id,
                                operation_name,
                                start_time,
                                duration,
                            ]
                        )


if __name__ == "__main__":

    trace_assembler = TraceAssembler("output.csv", 100000)
    loop = asyncio.get_event_loop()
    server = grpc.aio.server()

    async def serve():
        server.add_insecure_port("0.0.0.0:5555")
        trace_service_pb2_grpc.add_TraceServiceServicer_to_server(
            trace_assembler, server
        )
        await server.start()
        await trace_assembler.wait_count()
        await server.stop(5)

    try:
        loop.run_until_complete(serve())
        trace_assembler.close()
    finally:
        loop.close()
