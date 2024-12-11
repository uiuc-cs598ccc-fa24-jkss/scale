import asyncio
import grpc
import os
import sys
import pathlib

script_path = pathlib.Path(__file__).parent.resolve()
proto_path = os.path.join(script_path, "..", "..", "generated")
sys.path.append(proto_path)
from sampler.v1 import sampler_pb2, sampler_pb2_grpc

async def run():
    async with grpc.aio.insecure_channel("localhost:34317") as channel:
        stub = sampler_pb2_grpc.TraceSamplerStub(channel)
        request = sampler_pb2.SampleTracesDataRequest()
        async for response in stub.SampleTracesData(request):
            for resource_spans in response.resource_spans:
                for scope_spans in resource_spans.scope_spans:
                    for span in scope_spans.spans:
                        trace_id = bytes.hex(span.trace_id)
                        print(trace_id)

if __name__ == '__main__':
    asyncio.run(run())
