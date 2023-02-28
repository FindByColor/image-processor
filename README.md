![Find By Color Logo](https://findbycolor-github.s3.amazonaws.com/logo.png "Find By Color Logo")

Proof of Concept
===

> Web App & CLI for Find By Color Proof of Concept

Docker Usage
---

> If you would rather just use a Docker Container, we've got you covered.

**Requirements:**

- [X] [Docker Desktop](https://www.docker.com/products/docker-desktop/)

Build the Container

```bash
docker build -t fbc-process-image .
```

Running Container for CUDA Devices:

```bash
docker run --gpus=all -dp 8501:8501 fbc-process-image
```

Running Container for CPU Devices ( No CUDA ):
```
docker run -dp 8501:8501 fbc-process-image
```

Local Usage
---

> You can also just run this locally on your developer machine if it has Python installed.

**Requirements:**

- [X] [Python 3.9+](https://www.python.org/downloads/)

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Run as Interactive Web App

```bash
streamlit run app.py
```

Run as CLI Tool

```bash
python cli.py /path/to/image.jpg --output=/path/to/folder
```
