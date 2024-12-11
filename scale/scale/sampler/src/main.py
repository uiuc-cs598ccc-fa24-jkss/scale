import argparse
import asyncio
import logging
import faulthandler

import grpc
from opentelemetry.proto.collector.trace.v1 import trace_service_pb2_grpc
try:
    from sampler.v1 import sampler_pb2_grpc
except:
    from generated.sampler.v1 import sampler_pb2_grpc

from trace_handler import TraceSampler


def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max_train_duration",
        type=int,
        default=1000,
        help="Maximum duration to allow for training",
    )
    parser.add_argument(
        "--max_duration",
        type=int,
        default=5000,
        help="Cap for longest possible duration",
    )
    parser.add_argument(
        "--min_train_count",
        type=int,
        default=20,
        help="Minimum times training on an operation before we can begin to sample it",
    )
    parser.add_argument(
        "--min_score",
        type=float,
        default=0.60,
        help="Minimum score required for span to be sampled",
    )
    parser.add_argument(
        "--category_feature_length",
        type=int,
        default=8,
        help="Number of features to use for binary encoding of operation name",
    )
    parser.add_argument(
        "--train_size",
        type=int,
        default=2000,
        help="Number of traces to use for training",
    )
    parser.add_argument(
        "--tempo_url",
        type=str,
        default="http://tempo:3200",
        help="URL of Tempo REST endpoint",
    )
    parser.add_argument(
        "--listen_address",
        type=str,
        default="0.0.0.0:4317",
        help="host:port to bind gRPC server to",
    )
    parser.add_argument(
        "--start_delta",
        type=int,
        default=86400,
        help="Time interval in seconds before current time to start search for traces",
    )
    parser.add_argument(
        "--skip_span_count",
        type=int,
        default=20000,
        help="Skip the first n spans so that the otel collector doesn't flood the sampler",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    faulthandler.enable()
    config = get_config()
    loop = asyncio.get_event_loop()

    trace_sampler = TraceSampler(config)

    async def serve():
        server = grpc.aio.server()
        server.add_insecure_port(config.listen_address)
        trace_service_pb2_grpc.add_TraceServiceServicer_to_server(trace_sampler, server)
        sampler_pb2_grpc.add_TraceSamplerServicer_to_server(trace_sampler, server)
        await server.start()
        await server.wait_for_termination()

    loop.run_until_complete(trace_sampler.train())
    try:
        loop.run_until_complete(serve())
    finally:
        loop.close()
