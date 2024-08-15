# Use an official Python runtime as the base image
FROM --platform=linux/x86_64 python:3.11-slim

ENV TZ Asia/Tokyo
# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of the application code to the container
COPY . .

# Expose the port that the FastAPI application will run on
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
