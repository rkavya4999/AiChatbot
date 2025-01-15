# Use the official Python 3.12 image as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt requirements.txt

# Install system dependencies and Python dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Command to run the Streamlit app
CMD ["streamlit", "run", "test.py", "--server.port=8501", "--server.address=0.0.0.0"]
