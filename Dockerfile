FROM python:3.9

LABEL maintainer "Peter Schmalfeldt peter@findbycolor.com"
LABEL version="1.0"
LABEL description="Image Processor"
LABEL vendor="Find By Color"

# Set Working Directory
WORKDIR /fbc

# Copy Required Files
COPY app.py app.py
COPY batch.py batch.py
COPY cli.py cli.py
COPY requirements-dev.txt ./requirements-dev.txt
COPY requirements.txt ./requirements.txt

# Copy Required Folders
COPY .streamlit/ .streamlit/
COPY src/ src/

# Update Packages
RUN apt-get update && apt-get install -y build-essential curl software-properties-common git libgl1 && rm -rf /var/lib/apt/lists/*

# Install Python Dependencies
RUN pip3 install -r requirements-dev.txt
RUN pip3 install -r requirements.txt

# Expose Port used by Streamlit
EXPOSE 8501
