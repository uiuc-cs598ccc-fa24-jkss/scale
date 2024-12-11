import asyncio
import logging
import re
from typing import AsyncGenerator

import aioreactive as rx
from backends.tempo_client import TempoClient, TraceLimitException
from common.trace_util import extract_service
from opentelemetry.proto.collector.trace.v1 import (
    trace_service_pb2,
    trace_service_pb2_grpc,
)
from opentelemetry.proto.trace.v1.trace_pb2 import ResourceSpans, ScopeSpans, TracesData
from river import anomaly

try:
    from sampler.v1 import sampler_pb2, sampler_pb2_grpc
except:
    from generated.sampler.v1 import sampler_pb2, sampler_pb2_grpc

from tenacity import retry, wait_exponential

logger = logging.getLogger(__name__)


class TraceSampler(
    trace_service_pb2_grpc.TraceServiceServicer, sampler_pb2_grpc.TraceSampler
):

    SANITIZE_PATTERNS = [
        re.compile("(GET .*)\\?.*"),
        re.compile("(GET /api/products)/[A-Z0-9]+"),
    ]

    def __init__(self, config):
        self._tempo_client = TempoClient(config.tempo_url)
        self._start_delta = config.start_delta
        self._train_size = config.train_size
        self._min_train_count = config.min_train_count
        self._max_train_duration = config.max_train_duration
        self._max_duration = config.max_duration
        self._min_score = config.min_score
        self._category_feature_length = config.category_feature_length
        self._stream: rx.AsyncSubject[TracesData] = rx.AsyncSubject()
        self._total_span_count = 0
        self._sampled_span_count = 0
        self._skip_span_count = config.skip_span_count
        self._hst = anomaly.HalfSpaceTrees(
            seed=42, limits={"dur": (0, self._max_duration)}
        )
        self._seen_spans = {}
        self.service_encodings = {}
        self.operation_encodings = {}

    @staticmethod
    def find_service_name(resource_spans: ResourceSpans):
        for attribute in resource_spans.resource.attributes:
            if attribute.key == "service.name":
                return attribute.value
        return "unknown_service"

    @classmethod
    def sanitize_operation(cls, operation: str) -> str:
        """Sanitizes operation names by removing text unique to a particular request

        Args:
            operation (str): span operation name

        Returns:
            str: sanitized operation
        """        
        for pattern in cls.SANITIZE_PATTERNS:
            operation = pattern.sub("\\1", operation)
        return operation

    def featurize(self, service: str, operation: str) -> dict[str, str]:
        """Performs binary encoding to featurize the span operation name

        Args:
            service (str): span service
            operation (str): span name

        Returns:
            dict[str, int]: one-hot encoding of service and operation
        """        
        service_encoding = self.service_encodings.get(service)
        if service_encoding is None:
            self.service_encodings[service] = service_encoding = len(self.service_encodings)
        operation_encoding = self.operation_encodings.get(operation)
        if operation_encoding is None:
            self.operation_encodings[operation] = operation_encoding = len(self.operation_encodings)
        features = {f"s{service_encoding}": 1, f"o{operation_encoding}": 1}
        return features

    async def train(self) -> None:
        """Train model using traces pulled from Tempo"""

        logger.info("Starting training")

        @retry(wait=wait_exponential(multiplier=1, min=5, max=60))
        async def tempo_span_df():
            try:
                logger.info("Pulling spans from Tempo")
                return await self._tempo_client.build_span_df(
                    self._start_delta, self._train_size
                )
            except TraceLimitException as e:
                logger.warning("Trace limit not reached: %s", e)
                raise
            except Exception as e:
                logger.exception("Error retrieving training data:")
                raise

        spans = await tempo_span_df()
        root_spans = spans[spans.ParentID == "root"]
        spans = spans[spans.TraceID.isin(root_spans.TraceID)]
        for index, span in spans.iterrows():
            service = span["ServiceName"]
            operation = self.sanitize_operation(span["OperationName"])
            record = self.featurize(service, operation)
            duration = span["Duration"]
            record["dur"] = duration
            self._hst.learn_one(record)

        logger.info("Training complete")

    async def Export(
        self, request: trace_service_pb2.ExportTraceServiceRequest, context
    ) -> trace_service_pb2.ExportTraceServiceResponse:
        """Receive trace information from an OTLP upstream (usually an OTel Collector)

        Args:
            request (trace_service_pb2.ExportTraceServiceRequest): export request
            context (_type_): grpc context

        Returns:
            ExportTraceServiceResponse: export response
        """

        resource_spans_list = []
        for resource_spans in request.resource_spans:
            scope_spans_list = []
            for scope_spans in resource_spans.scope_spans:
                spans_list = []
                for span in scope_spans.spans:
                    scored = False
                    if self._skip_span_count:
                        self._skip_span_count -= 1
                        score = 0
                    else:
                        duration = 1e-6 * (
                            span.end_time_unix_nano - span.start_time_unix_nano
                        )
                        service = extract_service(resource_spans)
                        operation = self.sanitize_operation(span.name)
                        record = self.featurize(service, operation)
                        record["dur"] = duration
                        seen_count = self._seen_spans.get(operation, 0)
                        if seen_count < 20: 
                            if duration < self._max_train_duration:
                                self._hst.learn_one(record)
                                self._seen_spans[operation] = seen_count + 1
                            score = 1
                        else:
                            score = self._hst.score_one(record)
                            self._total_span_count += 1
                            scored = True

                    if score > self._min_score:
                        spans_list.append(span)
                        if scored:
                            self._sampled_span_count += 1
                            total_sample_rate = 100 * (
                                self._sampled_span_count / self._total_span_count
                            )
                            logger.info(
                                "Sampled %d of %d (%.1f%%) spans",
                                self._sampled_span_count,
                                self._total_span_count,
                                total_sample_rate,
                            )
                if spans_list:
                    scope_spans_list.append(
                        ScopeSpans(
                            scope=scope_spans.scope,
                            schema_url=scope_spans.schema_url,
                            spans=spans_list,
                        )
                    )
            if scope_spans_list:
                resource_spans_list.append(
                    ResourceSpans(
                        resource=resource_spans.resource,
                        schema_url=resource_spans.schema_url,
                        scope_spans=scope_spans_list,
                    )
                )

        if self._skip_span_count:
            logger.info("Skipping spans, %s remaining", self._skip_span_count)
        elif resource_spans_list:
            await self._stream.asend(TracesData(resource_spans=resource_spans_list))

        return trace_service_pb2.ExportTraceServiceResponse()

    async def SampleTraces(
        self, request: sampler_pb2.SampleTracesRequest, context
    ) -> AsyncGenerator[TracesData, None]:
        """_summary_

        Args:
            request (sampler_pb2.SampleTracesRequest): request object (ignored)
            context (_type_): grpc context

        Returns:
            AsyncGenerator[TracesData, None]: trace id generator

        Yields:
            Iterator[AsyncGenerator[TracesData, None]]: proto wrapper for trace ids
        """        
        logger.info("Client connected")

        observer = rx.AsyncIteratorObserver(self._stream)
        loop = asyncio.get_running_loop()

        def cancel(ctx):
            loop.create_task(observer.dispose_async())
            logger.info("Client closed")

        context.add_done_callback(cancel)

        async for traces_data in observer:
            for resource_spans in traces_data.resource_spans:
                for scope_spans in resource_spans.scope_spans:
                    for span in scope_spans.spans:
                        trace_id = bytes.hex(span.trace_id)
                        logger.info("Publishing %s to client", trace_id)
                        yield sampler_pb2.SampleTracesResponse(trace_id=trace_id)

    async def SampleTracesData(
        self, request: sampler_pb2.SampleTracesDataRequest, context
    ) -> AsyncGenerator[TracesData, None]:
        """_summary_

        Args:
            request (sampler_pb2.SampleTracesDataRequest): request object (ignored)
            context (_type_): grpc context

        Returns:
            AsyncGenerator[TracesData, None]: trace data generator

        Yields:
            Iterator[AsyncGenerator[TracesData, None]]: proto wrapper for trace data
        """        
        logger.info("Client connected")

        observer = rx.AsyncIteratorObserver(self._stream)
        loop = asyncio.get_running_loop()

        def cancel(ctx):
            loop.create_task(observer.dispose_async())
            logger.info("Client closed")

        context.add_done_callback(cancel)

        async for traces_data in observer:
            logger.info("Publishing traces data to client")
            yield traces_data
