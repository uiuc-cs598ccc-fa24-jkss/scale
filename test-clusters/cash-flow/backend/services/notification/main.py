from fastapi import FastAPI

from server.main import app as generated_app
from service import NotificationService
from health import HealthService

app = FastAPI()

app.mount("/internal/v1/notification", generated_app)
