# Tempo

## `search_traces`

```python
tempo_backend = TempoBackend(host='192.168.49.2', port=32000)

traces = backend.search_traces(
    service_name='Registration Service API',
    name='POST /enroll'
)

for trace in traces:
    print (trace)
```

Output

```bash
{'traceID': 'ff9be20d29b9142bb3201b152ba9bf0a', 'rootServiceName': 'Registration Service API', 'rootTraceName': 'POST /enroll', 'startTimeUnixNano': '1728101700231522077', 'durationMs': 799}
{'traceID': 'd890653268d69bbac43af4a8f97a7b43', 'rootServiceName': 'Registration Service API', 'rootTraceName': 'POST /enroll', 'startTimeUnixNano': '1728101699827739693', 'durationMs': 6}
{'traceID': '9e1f507f58ddabaaf2939c5de253feff', 'rootServiceName': 'Registration Service API', 'rootTraceName': 'POST /enroll', 'startTimeUnixNano': '1728101699820475457', 'durationMs': 7}
{'traceID': 'c87ab896613e5b4ed7e7014ec5ca4b08', 'rootServiceName': 'Registration Service API', 'rootTraceName': 'POST /enroll', 'startTimeUnixNano': '1728101699023249083', 'durationMs': 796}
{'traceID': '60cbd9fc7a1b7a541afdb32c88abb310', 'rootServiceName': 'Registration Service API', 'rootTraceName': 'POST /enroll', 'startTimeUnixNano': '1728101698621496447', 'durationMs': 6}
{'traceID': 'a0898f36deb3f4f10cdaf92db4a7df61', 'rootServiceName': 'Registration Service API', 'rootTraceName': 'POST /enroll', 'startTimeUnixNano': '1728101698614475411', 'durationMs': 6}
{'traceID': '8346bc11a47eb35279e7754a33e9ea8d', 'rootServiceName': 'Registration Service API', 'rootTraceName': 'POST /enroll', 'startTimeUnixNano': '1728101697829902763', 'durationMs': 783}
{'traceID': 'd76cd31113474e1af4c8d4b12cd41298', 'rootServiceName': 'Registration Service API', 'rootTraceName': 'POST /enroll', 'startTimeUnixNano': '1728101697428923047', 'durationMs': 7}
{'traceID': '59603f1a2bcc69fe38c3489aa1d963b3', 'rootServiceName': 'Registration Service API', 'rootTraceName': 'POST /enroll', 'startTimeUnixNano': '1728101697419391212', 'durationMs': 7}
{'traceID': 'd21dafee71ce1eb42bd3f31a4461b52c', 'rootServiceName': 'Registration Service API', 'rootTraceName': 'POST /enroll', 'startTimeUnixNano': '1728101697399937828', 'durationMs': 18}
```

Converted to pandas DataFrame

```python
trace_data = []
for trace in traces:
    trace_data.append({
        'traceID': trace['traceID'],
        'rootServiceName': trace['rootServiceName'],
        'rootTraceName': trace['rootTraceName'],
        'startTimeUnixNano': trace['startTimeUnixNano']
    })

trace_data_df = pd.DataFrame(trace_data)
print (trace_data_df)
```

```bash
                            traceID           rootServiceName rootTraceName    startTimeUnixNano
0  ff9be20d29b9142bb3201b152ba9bf0a  Registration Service API  POST /enroll  1728101700231522077
1  d890653268d69bbac43af4a8f97a7b43  Registration Service API  POST /enroll  1728101699827739693
2  9e1f507f58ddabaaf2939c5de253feff  Registration Service API  POST /enroll  1728101699820475457
3  c87ab896613e5b4ed7e7014ec5ca4b08  Registration Service API  POST /enroll  1728101699023249083
4  60cbd9fc7a1b7a541afdb32c88abb310  Registration Service API  POST /enroll  1728101698621496447
5  a0898f36deb3f4f10cdaf92db4a7df61  Registration Service API  POST /enroll  1728101698614475411
6  8346bc11a47eb35279e7754a33e9ea8d  Registration Service API  POST /enroll  1728101697829902763
7  d76cd31113474e1af4c8d4b12cd41298  Registration Service API  POST /enroll  1728101697428923047
8  59603f1a2bcc69fe38c3489aa1d963b3  Registration Service API  POST /enroll  1728101697419391212
9  d21dafee71ce1eb42bd3f31a4461b52c  Registration Service API  POST /enroll  1728101697399937828
```

## `get_trace_by_id`

Example:

```python
backend = TempoBackend(host='192.168.49.2', port=32000)
trace_data = backend.get_trace_by_id(tempo_backend, '4791e20d676f6eeeab951c62c408c987')

print (trace)
```

Output:

```bash
{'batches': [{'resource': {'attributes': [{'key': 'service.name', 'value': {'stringValue': 'Celery Task API'}}]}, 'scopeSpans': [{'scope': {'name': 'opentelemetry.instrumentation.fastapi', 'version': '0.48b0'}, 'spans': [{'traceId': 'R5HiDWdvbu6rlRxixAjJhw==', 'spanId': 'TNAaKat5i38=', 'parentSpanId': 'JL31w99qhc4=', 'name': 'GET /health http send', 'kind': 'SPAN_KIND_INTERNAL', 'startTimeUnixNano': '1728100561683684301', 'endTimeUnixNano': '1728100561684035666', 'attributes': [{'key': 'asgi.event.type', 'value': {'stringValue': 'http.response.start'}}, {'key': 'http.status_code', 'value': {'intValue': '200'}}], 'status': {}}, {'traceId': 'R5HiDWdvbu6rlRxixAjJhw==', 'spanId': 'nvecboOLIDw=', 'parentSpanId': 'JL31w99qhc4=', 'name': 'GET /health http send', 'kind': 'SPAN_KIND_INTERNAL', 'startTimeUnixNano': '1728100561684093174', 'endTimeUnixNano': '1728100561684126443', 'attributes': [{'key': 'asgi.event.type', 'value': {'stringValue': 'http.response.body'}}], 'status': {}}, {'traceId': 'R5HiDWdvbu6rlRxixAjJhw==', 'spanId': 'JL31w99qhc4=', 'name': 'GET /health', 'kind': 'SPAN_KIND_SERVER', 'startTimeUnixNano': '1728100561682432564', 'endTimeUnixNano': '1728100561684136464', 'attributes': [{'key': 'http.scheme', 'value': {'stringValue': 'http'}}, {'key': 'http.host', 'value': {'stringValue': '10.244.0.225:8000'}}, {'key': 'net.host.port', 'value': {'intValue': '8000'}}, {'key': 'http.flavor', 'value': {'stringValue': '1.1'}}, {'key': 'http.target', 'value': {'stringValue': '/internal/v1/tasks/health'}}, {'key': 'http.server_name', 'value': {'stringValue': '10.244.0.225:8000'}}, {'key': 'http.user_agent', 'value': {'stringValue': 'kube-probe/1.31'}}, {'key': 'net.peer.ip', 'value': {'stringValue': '10.244.0.1'}}, {'key': 'net.peer.port', 'value': {'intValue': '60846'}}, {'key': 'http.route', 'value': {'stringValue': '/health'}}, {'key': 'http.method', 'value': {'stringValue': 'GET'}}, {'key': 'http.url', 'value': {'stringValue': 'http://10.244.0.225:8000/internal/v1/tasks/health'}}, {'key': 'http.status_code', 'value': {'intValue': '200'}}], 'status': {}}]}]}]}
```

Converted to a pandas DataFrame

```python
spans_list = []

for batch in trace_data['batches']:
    resource = {attr['key']: attr['value']['stringValue'] for attr in batch['resource']['attributes']}
    for scopeSpan in batch['scopeSpans']:
        scope_name = scopeSpan['scope']['name']
        scope_version = scopeSpan['scope'].get('version', None)
        
        for span in scopeSpan['spans']:
            span_info = {
                'traceId': span['traceId'],
                'spanId': span['spanId'],
                'parentSpanId': span.get('parentSpanId'),
                'name': span['name'],
                'kind': span['kind'],
                'startTimeUnixNano': span['startTimeUnixNano'],
                'endTimeUnixNano': span['endTimeUnixNano'],
                'service_name': resource.get('service.name'),
                'scope_name': scope_name,
                'scope_version': scope_version,
            }
            
            # Extract span attributes
            for attribute in span['attributes']:
                key = attribute['key']
                value = attribute['value'].get('stringValue') or attribute['value'].get('intValue')
                span_info[key] = value
            
            spans_list.append(span_info)

trace_df = pd.DataFrame(spans_list)
print (trace_df)
```

```bash
                    traceId        spanId  parentSpanId                   name                kind    startTimeUnixNano      endTimeUnixNano  ... net.peer.ip net.peer.port http.route http.method                                           http.url http.status_code      asgi.event.type
0  R5HiDWdvbu6rlRxixAjJhw==  JL31w99qhc4=          None            GET /health    SPAN_KIND_SERVER  1728100561682432564  1728100561684136464  ...  10.244.0.1         60846    /health         GET  http://10.244.0.225:8000/internal/v1/tasks/health              200                  NaN
1  R5HiDWdvbu6rlRxixAjJhw==  TNAaKat5i38=  JL31w99qhc4=  GET /health http send  SPAN_KIND_INTERNAL  1728100561683684301  1728100561684035666  ...         NaN           NaN        NaN         NaN                                                NaN              200  http.response.start
2  R5HiDWdvbu6rlRxixAjJhw==  nvecboOLIDw=  JL31w99qhc4=  GET /health http send  SPAN_KIND_INTERNAL  1728100561684093174  1728100561684126443  ...         NaN           NaN        NaN         NaN                                                NaN              NaN   http.response.body
```
