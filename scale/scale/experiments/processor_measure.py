import asyncio
import time
import logging
import grpc
from opentelemetry.proto.collector.trace.v1 import (
    trace_service_pb2,
    trace_service_pb2_grpc,
)
from modeler.src.models import Trace
import asyncio
import aiohttp
from opentelemetry.proto.trace.v1.trace_pb2 import TracesData
from mock import MagicMock
import pathlib
import os
import sys

ITERATIONS = 100
TRACES = 200
FILE_PATH = pathlib.Path(__file__).parent.resolve()
TESTS_DIR = os.path.join(FILE_PATH, "..", "..", "..", "tests" )
print(FILE_PATH)
sys.path.append(os.path.join(FILE_PATH, "..", "modeler", "src"))
sys.path.append(os.path.join(FILE_PATH, "..", "orchestration", "src"))
logging.basicConfig(level=logging.ERROR)

from backends.tempo_client import TempoClient
from config.config_manager import ConfigManager
from modeler.src.trace_processor import TraceProcessor

async def main():

    config_path = os.path.join(TESTS_DIR , "configs", "otel-demo", "config.yaml")
    processor = TraceProcessor("", ConfigManager(config_path), MagicMock())

    client = TempoClient("http://localhost:32000")
    tcp_connection = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=tcp_connection) as session:
        query = '{.service.name != "otelgen"} && {trace:rootService != ""}'
        # query = '{name = "microservices"}'
        # query = '{name = "mobile_web"}'
        trace_ids = await client.search(session, (24*60*60), 200, query)
        traces_datas: list[TracesData] = [await client.find_trace_by_id(session, t_id) for t_id in trace_ids]
        start = time.time()
        for i in range(ITERATIONS):
            for td in traces_datas:
                trace = Trace.from_proto(trace_data=td)
                processor._process_trace(trace)
        end = time.time()
    print(f"{end - start}s elapsed for {len(traces_datas) * ITERATIONS} traces")
 

if __name__ == "__main__":

    asyncio.run(main())
# /home/moonkev/projects/cs598-project/scale/scale/experiments
# 0.23182964324951172s elapsed for 20000 traces
# (.venv)  moonkev@phantom  ~/projects/cs598-project/scale/scale   main ±  python -m experiments.processor_measure
# /home/moonkev/projects/cs598-project/scale/scale/experiments
# 56.80450797080994s elapsed for 20000 traces