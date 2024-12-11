import asyncio
import logging
import time
import urllib.parse

import pandas as pd
import aiohttp
from opentelemetry.proto.trace.v1.trace_pb2 import TracesData

from common.trace_util import TRACE_DF_COLUMNS, extract_spans


logger = logging.getLogger(__name__)


class TraceLimitException(Exception):
    """Exception for when the requested limit of traces is not met"""


class TempoClient:
    """Convenience class for interacting with Tempo gRPC API"""

    QUERY_HEADERS = {"Accept": "application/protobuf"}

    def __init__(self, tempo_url):
        self._tempo_url = tempo_url

    async def search(
        self,
        session: aiohttp.ClientSession,
        start_delta: int,
        limit: int,
        query: str,
    ) -> list[str]:
        """Search Tempo for arbitrary traces

        Args:
            session (aiohttp.ClientSession): aiohttp Session
            start_delta (int): Number of seconds in past to search for traces.
            limit (int): maximum among of traces to pull back from Tempo
        Returns:
            list[str]: trace ids from tempo meeting request criteria
        """
        logger.info("Searching tempo for %d traces", limit)
        end = int(time.time()) - 20
        start = end - start_delta
        traceql = urllib.parse.quote(query)
        url = f"{self._tempo_url}/api/search?q={traceql}&start={start}&end={end}&limit={limit}"
        async with session.get(url) as response:
            trace_data = await response.json()
            trace_ids = [t["traceID"] for t in trace_data["traces"]]
            logger.info("Trace search complete")
            return trace_ids

    async def find_trace_by_id(
        self, session: aiohttp.ClientSession, trace_id: str
    ) -> TracesData:
        """Find a trace in Tempo by it's trace id

        Args:
            session (aiohttp.ClientSession): aiohttp Session
            trace_id (str): ID of trace

        Returns:
            TraceByIDResponse: response from Tempo containing trace info
        """
        url = f"{self._tempo_url}/api/traces/{trace_id}"
        async with session.get(url, headers=self.QUERY_HEADERS) as response:
            message = TracesData()
            payload = await response.read()
            if response.status == 200:
                message.ParseFromString(payload)
            else:
                logger.warning(
                    "Could not retrieve trace with id %s: %s", trace_id, payload
                )
            return message

    async def build_span_df(
        self, start_delta: int, limit: int, query: str = '{trace:rootService != ""}'
    ) -> pd.DataFrame:
        """Generate a pandas data frame containing trace data in the following form
        [TraceID,SpanID,ParentID,OperationName,StartTimeUnixNano,Duration]

        Args:
            start_delta (int): Number of seconds in past to search for traces.
            limit (int): Limit number of records from Tempo. Defaults to 1000.

        Returns:
            pd.DataFrame: data frame containing trace data
        """

        tcp_connection = aiohttp.TCPConnector(limit=2)
        async with aiohttp.ClientSession(connector=tcp_connection) as session:
            trace_ids = await self.search(session, start_delta, limit, query)
            if len(trace_ids) < limit:
                raise TraceLimitException(
                    f"Requested {limit} traces but only {len(trace_ids)} were received"
                )
            tasks = [
                asyncio.ensure_future(self.find_trace_by_id(session, t_id))
                for t_id in trace_ids
            ]
            traces = await asyncio.gather(*tasks)

        span_extract = extract_spans(r for t in traces for r in t.resource_spans)
        df = pd.DataFrame(span_extract, columns=TRACE_DF_COLUMNS)
        return df
