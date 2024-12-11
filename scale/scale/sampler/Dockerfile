FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

ENV PYTHONPATH="${PYTHONPATH}:$(find /app -type d | tr '\n' ':')"

# Copy requirements.txt into the container at /app
COPY ./sampler/requirements.txt /app

# Upgrade pip
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the necessary ports
EXPOSE 4317

# Copy application contents
ADD ./sampler/src /app

# Copy common utilities
COPY ./common/__init__.py /app/common/__init__.py
COPY ./common/trace_util.py /app/common/trace_util.py

# Copy backend client
COPY ./backends/__init__.py /app/backends/__init__.py
COPY ./backends/tempo_client.py /app/backends/tempo_client.py

# copy the generated sampler to the app directory to satisfy the import
COPY ./generated/sampler /app/sampler

# Run the service when the container launches
CMD ["python", "main.py"]
