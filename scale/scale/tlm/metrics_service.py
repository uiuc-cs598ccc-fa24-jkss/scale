import logging
from google.protobuf.json_format import MessageToDict #, MessageToJson
from opentelemetry.proto.collector.metrics.v1 import metrics_service_pb2_grpc
from opentelemetry.proto.collector.metrics.v1 import metrics_service_pb2

def log_request(request):
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        # Detailed logging (DEBUG level): Log the entire message
        request_dict = MessageToDict(request, preserving_proto_field_name=True)
        logging.debug(f"Detailed Metrics request: {request_dict}")
    elif logging.getLogger().isEnabledFor(logging.INFO):
        # Basic logging (INFO level): Log only summary information
        logging.info(f"Received Metrics data with {len(request.resource_metrics)} metrics.")
       
class MetricsService(metrics_service_pb2_grpc.MetricsServiceServicer):
    async def Export(self, request, context):
        logging.info("Received metrics data:")
        log_request(request)
        return metrics_service_pb2.ExportMetricsServiceResponse()
