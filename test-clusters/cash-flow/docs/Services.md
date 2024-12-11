# Code Structure
The current services are built out from `openapi` generated apis.  See [openapi docs](https://learn.openapis.org/introduction.html).  

The `openapi-generator` will generate all of the boilerplate api code, and allows you to focus on the API's functionality.

Each service has a similar directory structure under **/backend/services/**

As an example, look at the `auth` service.  
```       
|   crud.py             <--- these are the only files created            
|   database.py
|   Dockerfile          <--- the Dockerfile for this service
|   main.py             <--- imports our implementation and mounts the generated application
|   models.py           
|   security.py
|   service.py          <--- This module has a class that extends the *_api_base.py class and implements the service
|   test.py
|
\---openapi             <--- everything under openapi is generated 
    |   .flake8
    |   .gitignore
    |   .openapi-generator-ignore
    |   docker-compose.yaml
    |   Dockerfile
    |   openapi.yaml
    |   pyproject.toml
    |   README.md
    |   requirements.txt
    |   setup.cfg
    |
    +---.openapi-generator
    |       FILES
    |       VERSION
    |
    +---src
    |   +---openapi_server
    |   |   \---impl
    |   |           __init__.py
    |   |
    |   \---server
    |       |   main.py
    |       |   security_api.py
    |       |
    |       +---apis
    |       |       auth_api.py             <--- routers for auth API
    |       |       auth_api_base.py        <--- base api
    |       |       health_api.py           <--- router for the health API
    |       |       health_api_base.py      <--- base health api
    |       |       __init__.py
    |       |
    |       \---models
    |               extra_models.py
    |               http_validation_error.py
    |               token.py
    |               token_authorization_response.py
    |               user.py
    |               user_create.py
    |               validation_error.py
    |               validation_error_loc_inner.py
    |               validation_response.py
    |               __init__.py
    |
    \---tests
            conftest.py
            test_auth_api.py
            test_health_api.py
```

## Implemention
The only requirement for implementing the service is to extend the base api and implement the endpoints.  

The base api provides an abstract method, such as: 
```python
    # auth_api_base.py

    async def post_api_auth_register(
        self,
        user_create: UserCreate,
    ) -> User:
        """Register a new user.  Args:     user (schemas.UserCreate): The user data to be registered.     db (Session, optional): The database session. Defaults to Depends(get_db).  Returns:     schemas.User: The registered user data.  Raises:     HTTPException: If the username is already registered."""
        ...
```

and a router in `<service>_api.py` or `default_api.py`:
```python
# auth_api.py

@router.post(
    "/register",
    responses={
        200: {"model": User, "description": "Successful Response"},
        422: {"model": HTTPValidationError, "description": "Validation Error"},
    },
    tags=["auth"],
    summary="Register User",
    response_model_by_alias=True,
)
async def post_api_auth_register(
    user_create: UserCreate = Body(None, description=""),
) -> User:
    """Register a new user.  Args:     user (schemas.UserCreate): The user data to be registered.     db (Session, optional): The database session. Defaults to Depends(get_db).  Returns:     schemas.User: The registered user data.  Raises:     HTTPException: If the username is already registered."""
    if not BaseAuthApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthApi.subclasses[0]().post_api_auth_register(user_create)
```

**Note** the last line: `return await BaseAuthApi.subclasses[0]().post_api_auth_register(user_create)`

So, it is receing the request anc passing it to the first registered subclass, which is what the `service.py` implements
```python 
import ...

class AuthService(BaseAuthApi):
...

    async def post_api_auth_register(
        self,
        user_create: UserCreate,
    ) -> User:
        """Register a new user.  Args:     user (schemas.UserCreate): The user data to be registered.     db (Session, optional): The database session. Defaults to Depends(get_db).  Returns:     schemas.User: The registered user data.  Raises:     HTTPException: If the username is already registered."""
        user_create.password = security.get_password_hash(user_create.password)
        user = crud.create_user(user=user_create)
        return user
...        
```

### Wiring in the implementation
To register the implementation as a subclass of the base api, it needs to be imported in the `main.py` module.

Example: 
```python 
...
from fastapi import FastAPI

from server.main import app as generated_app
from service import RegistrationService
from health import HealthService

app = FastAPI()

app.mount("/api/v1/registration", generated_app)
```



# How the code is generated
The `deploy.sh` script is currently used generate all of the service and client APIs. It does so using something like the following command: 
```bash
  # Deploy Auth Service   
  echo "Generating Auth Service APIs from OpenAPI"
  ${GENERATE_CMD} \
      -i ${AUTH_SERVICE_SPEC_FILE} \
      -g ${AUTH_SERVICE_GENERATOR} \
      -o ${AUTH_SERVICE_DEPLOY_DIR} \
      --template-dir ${AUTH_SERVICE_TEMPLATE_DIR} \
      --package-name server \
      --reserved-words-mappings date=date 
```

Unpacking the environment variables, it looks like this: 

```bash
java -jar openapi-generator-cli.jar generate \
    -i specs/api/v1/services/auth.yaml \
    -g python-fastapi \
    -o /backend/services/auth/openapi \
    --template-dir templates/services/auth \
    --package-name server \
    --reserved-words-mappings date=date
```

* There are several ways to get access to the openapi-generator cli, I chose to go with the java tool as it seemed the simplets and didn't require additional package installations other than downloading the jar.  Alternatives are using a openapi-generator docker container or `npm`
* The command line tool requires an openapi *spec* to generate the api from.  In this example, it is ***specs/api/v1/services/auth.yaml***


# Open API specs
These are yaml or json files that define your service.  Basically this is your service schema. 

Example:
```yaml
# auth.yaml
openapi: 3.1.0
info:
  title: Authorization Service API
  version: 0.1.0
  description: API for managing user authentication and authorization

servers:
  - url: /api/v1/auth
    description: Authorization Service Base URL

paths:
  /register:
    $ref: ../../paths/auth/register.yaml
  /token:
    $ref: ../../paths/auth/token.yaml
  /me:
    $ref: ../../paths/auth/me.yaml
  /health:
    $ref: ../../paths/health/health.yaml
  /authorize:
    $ref: ../../paths/auth/authorize.yaml
  /validate_user:
    $ref: ../../paths/auth/validate_user.yaml


components:
  securitySchemes:
    OAuth2PasswordBearer:
      type: oauth2
      flows:
        password:
          tokenUrl: /token
          scopes: {}
```

The `servers`, `paths` and `components` can be defined in this file, or referenced in other files as above.  

## Templates
The generator uses a set of default templates (`.mustache` files) for each of the files that are generated.  It uses a set of [default templates](https://github.com/OpenAPITools/openapi-generator/tree/master/modules/openapi-generator/src/main/resources/python-fastapi), but you can override these by providing a template directory with your local templates with this command:

example:
```bash
--template-dir templates/services/auth
```

### Template example 
**default**
```python
# coding: utf-8

{{>partial_header}}

from fastapi import FastAPI

{{#apiInfo}}
{{#apis}}
from {{apiPackage}}.{{classFilename}} import router as {{classname}}Router
{{/apis}}
{{/apiInfo}}

app = FastAPI(
    title="{{appName}}",
    description="{{appDescription}}",
    version="{{appVersion}}",
)

{{#apiInfo}}
{{#apis}}
app.include_router({{classname}}Router)
{{/apis}}
{{/apiInfo}}
```

**overridden**
```python
# coding: utf-8

{{>partial_header}}

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace

import os

{{#apiInfo}}
{{#apis}}
from {{apiPackage}}.{{classFilename}} import router as {{classname}}Router
{{/apis}}
{{/apiInfo}}

# Set up OpenTelemetry Tracer and Exporter
def configure_tracing(app):
    # Create the OTLP exporter to send traces to the OpenTelemetry Collector
    resource = Resource(attributes={
        SERVICE_NAME: "{{appName}}"
    })

    endpoint = os.getenv("OTEL_COLLECTOR_ENDPOINT", "otel-collector:4317")

    # Set up the tracer provider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Add a BatchSpanProcessor to process and export spans
    span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Instrument the FastAPI app and any outgoing HTTP requests via urllib3
    FastAPIInstrumentor.instrument_app(app)
    URLLib3Instrumentor().instrument()
    Psycopg2Instrumentor().instrument()

app = FastAPI(
    title="{{appName}}",
    description="{{appDescription}}",
    version="{{appVersion}}",
)

# Call the OpenTelemetry tracing configuration
configure_tracing(app)

{{#apiInfo}}
{{#apis}}
app.include_router({{classname}}Router)
{{/apis}}
{{/apiInfo}}
```




