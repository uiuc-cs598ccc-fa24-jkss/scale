# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: sampler/v1/sampler.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from opentelemetry.proto.trace.v1 import trace_pb2 as opentelemetry_dot_proto_dot_trace_dot_v1_dot_trace__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18sampler/v1/sampler.proto\x12\rscale.sampler\x1a(opentelemetry/proto/trace/v1/trace.proto\"\x15\n\x13SampleTracesRequest\"\x19\n\x17SampleTracesDataRequest\"(\n\x14SampleTracesResponse\x12\x10\n\x08trace_id\x18\x01 \x01(\t2\xd5\x01\n\x0cTraceSampler\x12[\n\x0cSampleTraces\x12\".scale.sampler.SampleTracesRequest\x1a#.scale.sampler.SampleTracesResponse\"\x00\x30\x01\x12h\n\x10SampleTracesData\x12&.scale.sampler.SampleTracesDataRequest\x1a(.opentelemetry.proto.trace.v1.TracesData\"\x00\x30\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'sampler.v1.sampler_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_SAMPLETRACESREQUEST']._serialized_start=85
  _globals['_SAMPLETRACESREQUEST']._serialized_end=106
  _globals['_SAMPLETRACESDATAREQUEST']._serialized_start=108
  _globals['_SAMPLETRACESDATAREQUEST']._serialized_end=133
  _globals['_SAMPLETRACESRESPONSE']._serialized_start=135
  _globals['_SAMPLETRACESRESPONSE']._serialized_end=175
  _globals['_TRACESAMPLER']._serialized_start=178
  _globals['_TRACESAMPLER']._serialized_end=391
# @@protoc_insertion_point(module_scope)
