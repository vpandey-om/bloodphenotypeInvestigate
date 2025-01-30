# Use Python 3.11 as the base image
FROM python:3.11

# Set the working directory
WORKDIR /code

# Copy the requirements file
COPY ./requirements.txt /code/requirements.txt

# Upgrade the system and install dependencies
RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r /code/requirements.txt
RUN pip install --no-cache-dir gunicorn openpyxl

# Copy application files
COPY ./app.py /code/
COPY ./assets/ /code/assets/
COPY ./components/ /code/components/
COPY ./data/ /code/data/
COPY ./utils/ /code/utils/

# Expose port 8000 for the application
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH /code
ENV GUNICORN_CMD_ARGS "--bind=0.0.0.0:8000 --workers=2 --threads=4 --worker-class=gthread --forwarded-allow-ips='*' --access-logfile -"

# Start the application using Gunicorn
CMD ["gunicorn", "app:server"]
