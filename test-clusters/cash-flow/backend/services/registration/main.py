from fastapi import FastAPI

from server.main import app as generated_app
from service import RegistrationService
from health import HealthService

app = FastAPI()

app.mount("/api/v1/registration", generated_app)
