# metrics.py

import time
import threading
import logging
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class Metrics:
    def __init__(self):
        self.traces_processed = 0
        self.trace_latencies = deque()
        self.span_durations = defaultdict(deque)
        self.service_latencies = defaultdict(lambda: {"latencies": deque(), "count": 0, "total_duration": 0})

    def record_trace_latency(self, duration):
        """Records the latency of a trace."""
        self.trace_latencies.append(duration)
        self.traces_processed += 1

    def record_span_duration(self, service, operation, duration):
        """Records the duration of a span for a specific service and operation."""
        self.span_durations[(service, operation)].append(duration)
        self.service_latencies[service]["latencies"].append(duration)
        self.service_latencies[service]["total_duration"] += duration
        self.service_latencies[service]["count"] += 1

    def get_average_trace_latency(self):
        """Calculates the average trace latency."""
        if not self.trace_latencies:
            return 0
        return sum(self.trace_latencies) / len(self.trace_latencies)

    def get_p_trace_latency(self, percentile):
        """
        Calculates a specific percentile of trace latency.

        Args:
            percentile (float): The percentile to calculate (e.g., 75, 90, 95).

        Returns:
            float: The specified percentile of trace latency.
        """
        if not self.trace_latencies:
            return 0
        return np.percentile(list(self.trace_latencies), percentile)

    def get_average_span_duration(self, service, operation):
        """Calculates the average span duration for a service operation."""
        durations = self.span_durations[(service, operation)]
        if not durations:
            return 0
        return sum(durations) / len(durations)

    def get_service_average_latency(self, service):
        """Calculates the average latency for a service."""
        service_data = self.service_latencies[service]
        if service_data["count"] == 0:
            return 0
        return service_data["total_duration"] / service_data["count"]

    def reset_metrics(self):
        """Reset all metrics (useful for periodic reporting)."""
        self.traces_processed = 0
        self.trace_latencies.clear()
        for key in self.span_durations:
            self.span_durations[key].clear()
        for key in self.service_latencies:
            self.service_latencies[key]["latencies"].clear()
            self.service_latencies[key]["count"] = 0
            self.service_latencies[key]["total_duration"] = 0


class MetricsReporter:
    def __init__(self, metrics: Metrics, report_interval=60):
        self.metrics = metrics
        self.report_interval = report_interval
        self._stop_event = threading.Event()
        self._report_thread = threading.Thread(target=self._report_metrics, daemon=True)

    def start(self):
        """Start reporting metrics at regular intervals."""
        self._report_thread.start()

    def stop(self):
        """Stop the reporting thread."""
        self._stop_event.set()
        self._report_thread.join()

    def _report_metrics(self):
        """Periodically log collected metrics."""
        while not self._stop_event.is_set():
            logger.info("=== Metrics Report ===")
            logger.info(f"Total traces processed: {self.metrics.traces_processed}")
            logger.info(f"Average trace latency: {self.metrics.get_average_trace_latency():.2f} ms")
            logger.info(f"75th percentile trace latency (p75): {self.metrics.get_p_trace_latency(75):.2f} ms")
            logger.info(f"90th percentile trace latency (p90): {self.metrics.get_p_trace_latency(90):.2f} ms")
            logger.info(f"95th percentile trace latency (p95): {self.metrics.get_p_trace_latency(95):.2f} ms")

            for (service, operation), durations in self.metrics.span_durations.items():
                avg_duration = self.metrics.get_average_span_duration(service, operation)
                logger.info(f"Service: {service} | Operation: {operation} | Average Span Duration: {avg_duration:.2f} ms")

            for service in self.metrics.service_latencies:
                avg_latency = self.metrics.get_service_average_latency(service)
                logger.info(f"Service: {service} | Average Latency: {avg_latency:.2f} ms")

            logger.info("=====================")
            self.metrics.reset_metrics()
            time.sleep(self.report_interval)
