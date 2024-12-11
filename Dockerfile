# Use an official Python image as a base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the local environment YAML file into the container
COPY environment.yml /app/environment.yml

# Copy your script and any other necessary files into the container
COPY BioDBTracker.py /app/BioDBTracker.py
COPY . /app

# Install system dependencies required by gspread and oauth2client
RUN apt-get update && apt-get install -y \
    libssl-dev \
    libffi-dev \
    libsqlite3-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Conda (Miniconda) for managing dependencies
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    /opt/conda/bin/conda init

# Add Conda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Create and activate the Conda environment
RUN conda env create -f /app/environment.yml && conda clean -a

# Activate the environment in the container
SHELL ["conda", "run", "-n", "BioDBTracker", "/bin/bash", "-c"]

# Set the default command 
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "BioDBTracker", "python", "/app/BioDBTracker.py"]



