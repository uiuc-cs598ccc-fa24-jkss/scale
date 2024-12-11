from tenacity import retry, wait_fixed, stop_never
import grpc
import asyncio
import os
import logging
try:
    from generated.sampler.v1 import sampler_pb2, sampler_pb2_grpc
except:
    from sampler.v1 import sampler_pb2, sampler_pb2_grpc
from trace_processor import TraceProcessor

logger = logging.getLogger(__name__)

class TraceConsumer:
    def __init__(self, processor: TraceProcessor):
        channel_address = os.getenv("TRACE_SAMPLER_CHANNEL", "sampler:4317")
        self._channel = grpc.aio.insecure_channel(channel_address)
        self._stub = sampler_pb2_grpc.TraceSamplerStub(self._channel)
        self._request = sampler_pb2.SampleTracesRequest()
        self._processor = processor
        self._connected = False

    @retry(
        wait=wait_fixed(5),
        stop=stop_never,
    )
    async def consume(self):
        while True:
            try:
                async for response in self._stub.SampleTraces(self._request):
                    if not self._connected:
                        logger.info(f"Connected established to channel: {os.getenv('TRACE_SAMPLER_CHANNEL', 'sampler:4317')}")
                        self._connected = True
                         
                        # start the processor task when the connection is established
                        asyncio.create_task(self._processor.start())

                    await self._processor.process(response)
            except grpc.aio.AioRpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    logger.warning(f"Server unavailable, retrying: {e.details()}")
                    raise  # Raise the error to trigger the retry
                else:
                    logger.error(f"Unexpected gRPC error: {e.details()}")
                    break  # Break the loop on unexpected errors

    async def close(self):
        await self._channel.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
