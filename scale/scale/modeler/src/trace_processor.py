import os
import aiohttp
import asyncio
from typing import Tuple, List
from opentelemetry.proto.trace.v1.trace_pb2 import TracesData
from google.protobuf.json_format import MessageToDict
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict

from models import Trace, LatencyTracker, LatencyAnalyzer
from backends.tempo_client import TempoClient
from config.config_interface import ConfigInterface
from metrics import Metrics, MetricsReporter
try:
    from orchestration_client import OrchestrationClient
except:
    from orchestration.orchestration_client import OrchestrationClient

logger = logging.getLogger(__name__)


class TraceProcessor:
    def __init__(self, client_url: str, config: ConfigInterface, orchestrator: OrchestrationClient):
        self._tempo_client = TempoClient(client_url)
        self._config = config
        self._orchestrator = orchestrator
        self._tracker = LatencyTracker()
        self._analyzer = LatencyAnalyzer(self._tracker)
        self._queue = asyncio.Queue()  
        if logger.isEnabledFor(logging.DEBUG):
            self._metrics = Metrics()
            self._metrics_reporter = MetricsReporter(self._metrics, report_interval=60)
            self._metrics_reporter.start()        

        logger.info ("TraceProcessor initialized")


    async def process(self, trace_data: TracesData):
        """
        Processes traces received from from the TraceConsumer
        Parses the TracesData object into a Trace object and 
        submits it to the processing queue for further analysis.
        """
        logger.info(f"Processing trace {trace_data.trace_id}")
        try: 
            trace_response = await self._query_trace_id(trace_id=trace_data.trace_id)
            trace = Trace.from_proto(trace_data=trace_response)

            self._tracker.track(trace)
            if logger.isEnabledFor(logging.DEBUG):
                # Record the trace latency for metrics
                trace_duration_ms = trace.duration_ms
                self._metrics.record_trace_latency(trace_duration_ms)

                # Record individual span latencies for metrics
                for span in trace.span_dict.values():
                    self._metrics.record_span_duration(span.service_name, span.name, span.duration_ms)                            
            logger.debug(f"_tracker: {self._tracker.service_data.keys()}")

            # Add the trace to the queue
            await self._queue.put(trace)
            logger.debug(f"Trace queued for processing: {trace.trace_id}")

        except Exception as e:
            logger.exception(f"Error processing trace: {trace_data.trace_id}, {e}")


    async def start(self):
        """
        Starts a background task to consume traces from the queue.
        """
        logger.info("Starting trace processor worker")
        while True:
            trace = await self._queue.get()  
            try:
                self._process_trace(trace)  
                logger.debug(f"Trace processed: {trace.trace_id}")
            except Exception as e:
                logger.exception(f"Error processing trace from queue: {trace.trace_id}, {e}")
            finally:
                self._queue.task_done()


    def _process_trace(self, trace: Trace):
        """
        Extract the service names and passes on for analysis
        We only want to analyze services included in this trace
        """
        services = {span.service_name for span in trace.span_dict.values()}
        self._analyze_services_hybrid_ewma_cusum(services=services)


    async def _query_trace_id(
            self, 
            trace_id: str
    ) -> TracesData:
        """
        Query Tempo for a trace by its ID
        """
        tcp_connection = aiohttp.TCPConnector(limit=20)
        async with aiohttp.ClientSession(connector=tcp_connection) as session:
            return  await self._tempo_client.find_trace_by_id(session=session, trace_id=trace_id)


    def _report_service_latencies(self, service_name: str):
        logger.debug(
            f"Service: {service_name}\n"
            f"Average latency: {self._analyzer.average_latency(service_name)}\n"
            f"p75 latency: {self._analyzer.p75_latency(service_name)}\n"
            f"Overall trend: {self._analyzer.trend(service_name)}\n"
            f"Overall trend cusum: {self._analyzer.trend_cusum(service_name)}\n"
            f"Overall trend ema: {self._analyzer.trend_ema(service_name)}\n"
            f"Operation averages: {self._analyzer.operation_average_latencies(service_name)}\n"
            f"Operation p75s: {self._analyzer.operation_p75_latencies(service_name)}\n"            
            f"Operation trends: {self._analyzer.operation_trends(service_name)}\n"
            f"Operation trends cusum: {self._analyzer.operation_trends_cusum(service_name)}\n"
            f"Operation trends ema: {self._analyzer.operation_trends_ema(service_name)}\n"
        )


    def _analyze_services(self):
        """
        Iterate over all services and analyze their latencies
        If services average latency is above or below the threshold, scale up or down
        The average latency is calculated over the previous n traces, where n is max(10, queue_length)
        """
        for service_name in self._tracker.service_data:
            
            # We only care about configured services
            if service_name in self._config.get_all_resources():
                if self._tracker.queue_length(service_name) >= 10:  # arbitrary threshold
                    latency_threshold = self._config.get_latency_threshold(resource=service_name)    

                    # make sure a threshold is defined
                    if latency_threshold:
                        upper_bound = latency_threshold.get('upperBound')
                        lower_bound = latency_threshold.get('lowerBound')
                        avg_service_latency = self._analyzer.average_latency(service_name)

                        if avg_service_latency > upper_bound.get('value'):
                            logger.info(f"Service: {service_name}, Avg. Latency: {avg_service_latency} is ABOVE the upper bound of {upper_bound.get('value')}{upper_bound.get('units')}")
                            self._report_service_latencies(service_name)
                            logger.info(f"Scaling up service: {service_name}")
                            # self._orchestrator.scale_up(service_name)
                        elif avg_service_latency < lower_bound.get('value'):
                            logger.info(f"Service: {service_name}, Latency: {avg_service_latency} is BELOW the lower bound of {lower_bound.get('value')}{lower_bound.get('units')}")
                            self._report_service_latencies(service_name)
                            logger.info(f"Scaling down service: {service_name}")
                            # self._orchestrator.scale_down(service_name)
                        else:
                            logger.info(f"Service: {service_name}, Latency: {avg_service_latency} is within the bounds of {lower_bound.get('value')}{lower_bound.get('units')} and {upper_bound.get('value')}{upper_bound.get('units')}")
                    else: 
                        logger.warning(f"No latency threshold defined for service: {service_name}")

    def _hybrid_detection(self, service_name, latencies, span_threshold=None,   cusum_threshold=None, ewma_multiplier=1.5) -> Tuple[int, float, float, float, int, float, bool, bool]:
        """
        Hybrid detection method using EWMA for immediate responsiveness and CUSUM for sustained shifts.
        Determines if a service should scale up or down based on recent latency data.
        
        Returns:
            Tuple[int, float, float, float, int, bool, bool]: A tuple containing:
                - int: Action indicator (0 = no action, 1 = scale up, -1 = scale down)
                - float: Upper bound (in milliseconds)
                - float: Lower bound (in milliseconds)
                - float: Value triggering the action (either latency or CUSUM)
                - int: Span size
                - float: cusum threshold -x to x
                - bool: Triggered by EMA (True if due to EMA bounds, False otherwise)
                - bool: Triggered by CUSUM (True if due to CUSUM threshold, False otherwise)
        """
        
        # Set default span to one-third of queue length if not specified
        if span_threshold is None:
            span_threshold = max(1, len(latencies) // 3)  # Set span to one-third of current queue length, minimum 1

        if cusum_threshold is None:
            cusum_threshold = 1.5 * np.std(latencies[-span_threshold:])
            
        if len(latencies) < span_threshold:
            logging.warning("Not enough data to perform hybrid detection.")
            return 0, float('inf'), float('-inf'), float('nan'), span_threshold, cusum_threshold, False, False  # No action, with placeholder bounds

        # Full EWMA series and p75 of EWMA values
        ema_series = pd.Series(latencies).ewm(span=span_threshold, adjust=False).mean()
        ema_p75 = np.percentile(ema_series, 75)

        # Bounds using p75 of EWMA as the center point
        upper_bound = ema_p75 + ewma_multiplier * np.std(latencies[-span_threshold:])
        lower_bound = max(1, ema_p75 - ewma_multiplier * np.std(latencies[-span_threshold:]))  # Constrain lower_bound to non-negative values

        value = self._analyzer.p75_latency(service_name)  # Using p75 latency

        # CUSUM for sustained trend detection
        cusum = np.cumsum(np.array(latencies) - ema_p75)


        if value > upper_bound:# or cusum[-1] > cusum_threshold:
            return 1, upper_bound, lower_bound, value if value > upper_bound else cusum[-1], span_threshold, cusum_threshold, value > upper_bound, cusum[-1] > cusum_threshold  # Scale up
        elif value < lower_bound:# or cusum[-1] < -cusum_threshold:
            return -1, upper_bound, lower_bound, value if value < lower_bound else cusum[-1], span_threshold, cusum_threshold,  value < lower_bound, cusum[-1] < -cusum_threshold  # Scale down
        return 0, upper_bound, lower_bound, value, span_threshold, cusum_threshold, False, False  # No action


    def _analyze_services_hybrid_ewma_cusum(self, services: List[str]):
        """
        Analyze services using the hybrid detection method to see if they need scaling up or down.
        This method uses both EWMA for immediate responsiveness and CUSUM for sustained shifts.
        Logs information on scaling actions based on detected trends, with detailed latency metrics.
        """
        for service_name in services:
            latencies = self._tracker.get_latencies(service_name)

            # Check if there is enough data to proceed
            if not latencies:
                logging.warning(f"No latency data available for service: {service_name}")
                continue

            # Get the detection result from the hybrid detection function
            action, upper_bound, lower_bound, value, span_threshold, cume_threshold, is_ema, is_cusum = self._hybrid_detection(service_name, latencies)

            # Log and take action based on the detected need for scaling
            if action == 1:  # Scale up
                self._report_service_latencies(service_name)
                logging.info(f"Scaling up service: {service_name} | Lower Bound: {lower_bound} | Upper Bound {upper_bound} | span_threshold {span_threshold} | Due to ema: {is_ema} , {value} | Due to cusum: {is_cusum} , {value}, threshold {cume_threshold}")
                # self._orchestrator.scale_up(service_name)
            elif action == -1:  # Scale down
                self._report_service_latencies(service_name)
                logging.info(f"Scaling down service: {service_name} | Lower Bound: {lower_bound} | Upper Bound {upper_bound} | span_threshold {span_threshold} | Due to ema: {is_ema} , {value} | Due to cusum: {is_cusum} , {value}, threshold {cume_threshold}")
            else:  # No action
                logging.debug(f"No action service: {service_name} | Lower Bound: {lower_bound} | Upper Bound {upper_bound} | span_threshold {span_threshold} | Due to ema: {is_ema} , {value} | Due to cusum: {is_cusum} , {value}, threshold {cume_threshold}")

    def stop_metrics_reporting(self):
        """
        Stops the metrics reporting thread.
        """
        if logger.isEnabledFor(logging.DEBUG):
            self._metrics_reporter.stop()
