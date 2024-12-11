import logging

from google.protobuf.json_format import MessageToDict #, MessageToJson

from opentelemetry.proto.collector.logs.v1 import logs_service_pb2_grpc
from opentelemetry.proto.collector.logs.v1 import logs_service_pb2

def log_request(request):
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        # Detailed logging (DEBUG level): Log the entire message
        request_dict = MessageToDict(request, preserving_proto_field_name=True)
        logging.debug(f"Detailed Log request: {request_dict}")
    elif logging.getLogger().isEnabledFor(logging.INFO):
        # Basic logging (INFO level): Log only summary information
        logging.info(f"Received Log data with {len(request.resource_logs)} logs.")

class LogService(logs_service_pb2_grpc.LogsServiceServicer):
    async def Export(self, request, context):
        logging.info("Received log data:")
        log_request(request)
        return logs_service_pb2.ExportLogsServiceResponse()