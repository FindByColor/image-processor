FROM python:3.9

LABEL maintainer "Peter Schmalfeldt peter@findbycolor.com"
LABEL version="1.0"
LABEL description="Proof of Concept"
LABEL vendor="Find By Color"

WORKDIR /app
COPY requirements.txt ./requirements.txt

RUN apt-get update && apt-get install -y build-essential curl software-properties-common git libgl1 && rm -rf /var/lib/apt/lists/*

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]