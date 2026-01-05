# Use a slim version of Python for efficiency
FROM python:3.11-slim

# Install system dependencies for MySQL client
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Command to run the "Indo-Global" platform
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]