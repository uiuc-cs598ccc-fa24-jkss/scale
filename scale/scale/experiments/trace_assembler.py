import asyncio
import timeit

import grpc
from opentelemetry.proto.collector.trace.v1 import (
    trace_service_pb2,
    trace_service_pb2_grpc,
)
from opentelemetry.proto.trace.v1.trace_pb2 import ResourceSpans, ScopeSpans, TracesData


class TraceAssembler(trace_service_pb2_grpc.TraceServiceServicer):

    def __init__(self):
        self.traces = {}

    async def Export(
        self, request: trace_service_pb2.ExportTraceServiceRequest, context
    ):
        for resource_span in request.resource_spans:
            for scope_span in resource_span.scope_spans:
                for span in scope_span.spans:
                    item = (span, scope_span, resource_span)
                    if span.trace_id not in self.traces:
                        self.traces[span.trace_id] = [item]
                    else:
                        self.traces[span.trace_id].append(item)

    def assemble(self):

        def _asm():
            traces = []
            for trace_spans in self.traces.values():
                trace_data_resource_spans = []
                for span, scope_spans, resource_spans in trace_spans:
                    trace_data_resource_spans.append(
                        ResourceSpans(
                            resource=resource_spans.resource,
                            schema_url=resource_spans.schema_url,
                            scope_spans=[
                                ScopeSpans(
                                    scope=scope_spans.scope,
                                    schema_url=scope_spans.schema_url,
                                    spans=[span],
                                )
                            ],
                        )
                    )
                traces.append(TracesData(resource_spans=trace_data_resource_spans))

        t_seconds = timeit.timeit(_asm, number=1)
        print(
            f"Took {t_seconds}s for {len(self.traces)} - Average {t_seconds / len(self.traces)}s"
        )


if __name__ == "__main__":

    trace_assembler = TraceAssembler()
    loop = asyncio.get_event_loop()
    server = grpc.aio.server()

    async def serve():
        server.add_insecure_port("0.0.0.0:5555")
        trace_service_pb2_grpc.add_TraceServiceServicer_to_server(
            trace_assembler, server
        )
        await server.start()
        await asyncio.sleep(500)
        await server.stop(5)

    try:
        loop.run_until_complete(serve())
        trace_assembler.assemble()
    finally:
        loop.close()
