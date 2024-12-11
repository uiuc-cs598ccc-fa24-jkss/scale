import asyncio
import aiohttp
from backends.tempo_client import TempoClient
from opentelemetry.proto.trace.v1.trace_pb2 import TracesData

async def main():
    client = TempoClient("http://localhost:32000")
    tcp_connection = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=tcp_connection) as session:
        trace_ids = await client.search(session, (24*60*60), 2000)
        traces: list[TracesData] = [await client.find_trace_by_id(session, t_id) for t_id in trace_ids]
        total_size = 0
        for trace in traces:
            total_size += trace.ByteSize()
        print(f"{len(traces)} with size = {total_size}")

if __name__ == "__main__":
    asyncio.run(main())


        
