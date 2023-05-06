![Find By Color Logo](https://findbycolor-github.s3.amazonaws.com/logo.png 'Find By Color Logo')

**[↤ BACK](../README.md)**

# Local Install

> If you would prefer to run things locally, you can do that as well.

### Setup Development Environment

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Since we are using Python 3.9, you may need to specify the version of python when creating the virtual environment:

```bash
python3.9 -m venv venv
```

To exit the Python Virtual Environment, type the following into terminal:

```bash
deactivate
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
