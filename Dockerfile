# Use Python as the base image
FROM python:3.9-slim

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the app directory into the container
COPY app/ /app/

# Install required Python packages
RUN pip install requests

# envs
ARG CLOUDFLARE_API_TOKEN
ARG ZONE_ID

ENV CLOUDFLARE_API_TOKEN=${CLOUDFLARE_API_TOKEN}
ENV ZONE_ID=${ZONE_ID}

# Copy the cron job file
COPY cronjob /etc/cron.d/cronjob

# Give execution rights to the cron job
RUN chmod 0644 /etc/cron.d/cronjob

# Apply the cron job
RUN crontab /etc/cron.d/cronjob

# Create a log file to view cron logs
RUN touch /var/log/cron.log

# Start the cron service in the foreground
CMD printenv > /etc/environment && cron && tail -f /var/log/cron.log
