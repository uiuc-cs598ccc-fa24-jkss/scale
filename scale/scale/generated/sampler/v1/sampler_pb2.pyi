from opentelemetry.proto.trace.v1 import trace_pb2 as _trace_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SampleTracesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SampleTracesDataRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SampleTracesResponse(_message.Message):
    __slots__ = ("trace_id",)
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    trace_id: str
    def __init__(self, trace_id: _Optional[str] = ...) -> None: ...
