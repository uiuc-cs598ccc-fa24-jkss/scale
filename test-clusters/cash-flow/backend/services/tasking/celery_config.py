# celery_config.py
from celery import Celery
from opentelemetry.instrumentation.celery import CeleryInstrumentor


app = Celery(
    'tasking_service',
    broker='redis://redis:6379/0',  # Redis as the broker
    backend='redis://redis:6379/0',  # Redis as the result backend (optional)
    include=['tasks']  # Include the tasks module
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

CeleryInstrumentor().instrument()

if __name__ == '__main__':
    app.start()