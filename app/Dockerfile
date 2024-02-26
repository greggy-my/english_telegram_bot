# Use Python 3.9 image as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project directory into the container at /app
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-venv \
 && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv venv
RUN . venv/bin/activate
ENV PATH="/app/venv/bin:$PATH"
ENV ADMIN=''
ENV TOKEN=''

# Install Python dependencies
RUN pip install --no-cache-dir -r app/requirements.txt

# Command to run the application
CMD ["python", "bot.py"]

