![Find By Color Logo](https://findbycolor-github.s3.amazonaws.com/logo.png 'Find By Color Logo')

**[↤ BACK](../README.md)**

# Using Docker

> Docker ensures everything is preconfigured, set up, and ready to go.

**Requirements**:

-   [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## New Container

Run the following terminal command from the root of this project:

```bash
docker build --no-cache -t image-processor .
```

### Run Interactive Web App

This will start an interactive web application that runs on your local computer at http://127.0.0.1:8501

```bash
docker run --name fbc --rm -p 8501:8501 image-processor streamlit run app.py
```

### Run CLI for Single Image Processing

You can process a single image using the `cli.py` script.

```bash
docker run --name fbc --rm -v "$(pwd)"/data:/fbc/data image-processor python3 cli.py --help
docker run --name fbc --rm -v "$(pwd)"/data:/fbc/data image-processor python3 cli.py /fbc/data/input/image.jpg --dest=/fbc/data/output/ --json --images
```

### Run CLI for Batch Image Processing

To batch process everything in the `data/input` folder, use the `batch.py` script.

```bash
docker run --name fbc --rm -v "$(pwd)"/data:/fbc/data image-processor python3 batch.py --help
docker run --name fbc --rm -v "$(pwd)"/data:/fbc/data image-processor python3 batch.py --json --images
```

### Run Docker in CUDA Mode

If you are on a high-end computer with an Nvidia Graphics Card that supports CUDA, you can add the `--gpus=all` to `docker run` to enable CUDA support.  Just replace `docker run` with `docker run --gpus=all`
