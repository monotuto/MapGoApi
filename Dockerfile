# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (osmium-tool for fast PBF processing, wget for downloading)
RUN apt-get update && apt-get install -y \
    osmium-tool \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file into the container
COPY ./app/requirements.txt /code/requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY ./app /code/app
COPY ./entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh

# Create data directory
RUN mkdir -p /code/data

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
ENTRYPOINT ["/code/entrypoint.sh"]
