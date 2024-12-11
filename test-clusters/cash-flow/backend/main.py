from fastapi import FastAPI

# Import the configuration file
# atm this file is importing the Services to be used to 
# ensure they are registered as subclasses of the generated
# Base*Api classes
# Note: to register a new service, the config file must be updated
import config 

# Now import the generated app
from openapi_server.main import app as generated_app

# Create your main FastAPI application
app = FastAPI()

# Mount the generated app under the root path of the main application
app.mount("/", generated_app)
