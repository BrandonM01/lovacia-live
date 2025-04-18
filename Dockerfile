# Use the official Python image from the DockerHub as the base image
FROM python:3.11-slim

# Install system dependencies, including ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt into the container
COPY requirements.txt .

# Install Python dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application into the container
COPY . /app

# Expose port 10000 to the outside world
EXPOSE 10000

# Start the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
