FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Install required system dependencies for moviepy (including ffmpeg)
RUN apt-get update && apt-get install -y ffmpeg

# Install pip requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app

# Expose port 10000
EXPOSE 10000

# Start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
