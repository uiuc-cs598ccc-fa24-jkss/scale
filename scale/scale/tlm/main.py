import grpc
import asyncio
import logging
import os

from opentelemetry.proto.collector.trace.v1 import trace_service_pb2_grpc
from opentelemetry.proto.collector.logs.v1 import logs_service_pb2_grpc
from opentelemetry.proto.collector.metrics.v1 import metrics_service_pb2_grpc

from trace_service import TraceService
from log_service import LogService
from metrics_service import MetricsService


# run gRPC servers for traces, logs, and metrics
async def serve():

    server = grpc.aio.server()
    
    # Add TraceService to the server
    trace_service_pb2_grpc.add_TraceServiceServicer_to_server(TraceService(), server)
    server.add_insecure_port('[::]:4317')  # Trace OTLP gRPC port

    # Add LogService to the server
    logs_service_pb2_grpc.add_LogsServiceServicer_to_server(LogService(), server)
    server.add_insecure_port('[::]:4318')  # Log OTLP gRPC port

    # Add MetricsService to the server
    metrics_service_pb2_grpc.add_MetricsServiceServicer_to_server(MetricsService(), server)
    server.add_insecure_port('[::]:4319')  # Metrics OTLP gRPC port

    await server.start()
    logging.info("gRPC servers for traces (4317), logs (4318), and metrics (4319) started...")
    await server.wait_for_termination()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Start the gRPC servers for traces, logs, and metrics
    asyncio.run(serve())
