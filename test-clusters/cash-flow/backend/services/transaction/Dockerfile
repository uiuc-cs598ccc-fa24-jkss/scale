# Start from an official Python 3.9 image
FROM python:3.9-slim

# # Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Set the PYTHONPATH environment variable
ENV PYTHONPATH="/app/openapi/src"
ENV PYTHONPATH="${PYTHONPATH}:/app/interfaces/internal/tasking"
ENV PYTHONPATH="${PYTHONPATH}:/app/interfaces/internal/dms"
ENV PYTHONPATH="${PYTHONPATH}:/app/interfaces/internal/auth"
ENV PYTHONPATH="${PYTHONPATH}:/app/app_logging"
ENV PYTHONPATH="${PYTHONPATH}:/app:$PYTHONPATH"

# Upgrade pip
RUN pip install --upgrade pip

# Copy the requirements file to the working directory
COPY services/tasking/requirements.txt /app/
COPY otel-requirements.txt /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r otel-requirements.txt

COPY services/transaction/main.py /app/
COPY services/transaction/service.py /app/
COPY services/transaction/openapi /app/openapi
COPY common/health/health.py /app/
COPY interfaces/internal/dms/ /app/interfaces/internal/dms/
COPY interfaces/internal/tasking/ /app/interfaces/internal/tasking/
COPY interfaces/internal/auth/ /app/interfaces/internal/auth/
COPY app_logging/ /app/app_logging/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]