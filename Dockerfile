
# Use an official lightweight Python image as base
FROM python:3.10-slim

# Install Git and OpenSSH client
RUN apt-get update && \
    apt-get install -y git openssh-client && \
    rm -rf /var/lib/apt/lists/*

# Create SSH directory
RUN mkdir -p /root/.ssh

# Copy SSH private key and known_hosts file into the container
# These files should be placed in the same directory as the Dockerfile before building
COPY id_rsa /root/.ssh/id_rsa
COPY known_hosts /root/.ssh/known_hosts

# Set proper permissions for the SSH key
RUN chmod 600 /root/.ssh/id_rsa

# Clone the Bitbucket repository using SSH
RUN git clone git@bitbucket.org:your-username/your-repo.git /app

# Set working directory
WORKDIR /app
