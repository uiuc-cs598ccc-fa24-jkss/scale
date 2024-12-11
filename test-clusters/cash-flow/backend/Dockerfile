# Start from an official Python 3.9 image
FROM python:3.9-slim

# # Set environment variables
 ENV PYTHONUNBUFFERED=1 \
     PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Set the PYTHONPATH environment variable
ENV PYTHONPATH="/app/generated/src:/app:$PYTHONPATH"

# Upgrade pip
RUN pip install --upgrade pip

# Copy the requirements file to the working directory
COPY requirements.txt /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code to the container
# COPY . /app/
COPY main.py /app/
COPY config.py /app/
COPY generated /app/generated
COPY services /app/services
COPY tasking /app/tasking

# Expose the port the app runs on
EXPOSE 8000

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "openapi.src.openapi_server.main:app", "--host", "0.0.0.0", "--port", "8000"]