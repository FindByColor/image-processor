![Find By Color Logo](https://findbycolor-github.s3.amazonaws.com/logo.png "Find By Color Logo")

Proof of Concept
===

> Web App & CLI for Find By Color Proof of Concept

Docker Usage
---

If you would rather just use a Docker Container, we've got you covered.

<details>
    <summary>VIEW INSTRUCTIONS</summary>

---

**Requirements:**

- [X] [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Create Docker Image

This will build the image so you can spin it up as needed.

```bash
docker build --no-cache -t proof-of-concept .
```

### Run Interactive Web App

This will start an interactive web application that runs on your local computer at http://127.0.0.1:8501

```bash
docker run --name fbc --rm -p 8501:8501 proof-of-concept streamlit run app.py
```

### Run CLI for Single Image Processing

You can process a single image using the `cli.py` script.

NOTE: Change `"$(pwd)"/data` to your local path to `data` folder if executing outside of this project directory.

```bash
docker run --name fbc --rm -v "$(pwd)"/data:/fbc/data proof-of-concept python3 cli.py --help
docker run --name fbc --rm -v "$(pwd)"/data:/fbc/data proof-of-concept python3 cli.py /fbc/data/input/image.jpg --dest=/fbc/data/output/ --json --images
```

### Run CLI for Batch Image Processing

To batch process everything in the `data/input` folder, use the `batch.py` script. 

NOTE: Change `"$(pwd)"/data` to your local path to `data` folder if executing outside of this project directory.

```bash
docker run --name fbc --rm -v "$(pwd)"/data:/fbc/data proof-of-concept python3 batch.py --help
docker run --name fbc --rm -v "$(pwd)"/data:/fbc/data proof-of-concept python3 batch.py --json --images
```

### Run Docker in CUDA Mode

If you are on a high-end computer with an Nvidia Graphics Card that supports CUDA, you can add the `--gpus=all` to `docker run` to enable CUDA support.  Just replace `docker run` with `docker run --gpus=all`

</details>

Local Install
---

If you would prefer to run things locally, you can do that as well.

<details>
    <summary>VIEW INSTRUCTIONS</summary>

---

### Setup Development Environment

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

### Run Interactive Web App

This will start an interactive web application that runs on your local computer at http://127.0.0.1:8501

```bash
streamlit run app.py
```

### Run CLI for Single Image Processing

You can process a single image using the `cli.py` script.

```bash
python3 cli.py --help
python3 cli.py data/input/image.jpg --dest=data/output/ --json --images
```

### Run CLI for Batch Image Processing

To batch process everything in the `data/input` folder, use the `batch.py` script.

```bash
python3 batch.py --help
python3 batch.py --json --images
```

Windows WSL:
---

> You will likely need to run this command before you can run the install process ( replace `3.9` in `python3.9-venv` with your machines version of python )

```bash
sudo apt install python3.9-venv
```

</details>