from fastapi import FastAPI

from server.main import app as generated_app

from service import TaskingService
from health import HealthService

app = FastAPI()


app.mount("/internal/v1/tasks", generated_app)
