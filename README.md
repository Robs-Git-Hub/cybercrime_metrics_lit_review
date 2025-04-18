# J-G Jupyter Starter Docker Template

This repository provides a minimal starter template for running Jupyter Notebook in Docker, with Poetry used to manage your Python dependencies. It leverages the [Jupyter Docker Stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/index.html) **minimal-notebook** image as its foundation, which includes a pre-configured environment for Jupyter applications.

## Overview

The template is built on three layers provided by the official Jupyter Docker Stacks:

1. **Foundation:** A base Ubuntu image with core configurations.
2. **Base Notebook Stack:** Sets up system Python, user configurations, and Micromamba/Conda.
3. **Minimal-Notebook:** Provides a minimal Jupyter Notebook/Lab environment with essential tools and utilities (e.g., `curl`, `git`, `nano-tiny`, etc.).

This repository extends the minimal-notebook stack by adding a personalized Docker layer (`Dockerfile.dev`) that integrates Poetry. This enables you to manage and customize additional Python package dependencies without interfering with the core Jupyter installation.

## Features

- **Consistent Jupyter Environment:** Inherits from the well-maintained [minimal-notebook Docker image](https://github.com/jupyter/docker-stacks/tree/main/images/minimal-notebook).
- **Dependency Management with Poetry:** Leverages Poetry to ensure compatibility of your project’s dependencies.
- **Customizable Python Version:** The Dockerfile uses the `PYTHON_VERSION` build argument to specify the Python version (default is Python 3.11), making it easy to switch if needed.
- **Documentation and Reference:** This README includes instructions for building, running, and further customizing your environment.

## Getting Started

### Prerequisites

- **Docker:** Ensure Docker is installed and running on your system.
- **Docker Compose (optional):** For managing multi-container setups.
- **Poetry:** While Poetry is installed in the Docker image, you can also install it locally for managing your project dependencies.

### Creating the base-env.txt file

The requirements.txt file and base-env.txt are generated by running the lock.sh file with the command in terminal:
    bash lock.sh

You will only need to update the base-env.txt file, by running lock.sh again, if you change the jupyter docker stack used in the FROM part of the Dockerfile.dev.

Otherwise the only changes needed to dependencies are to add new ones to the requirements.in file.

### Initialising poetry

Poerty is installed when the image builds from the Dockerfile.dev.  

Its then necessary as part of the one-time initial set up to create a pyproject.toml.

To create the pyproject.toml first run the docker image such that it opens to bash terminal and not running jupyter.

```cmd
docker run -it --rm -v "%cd%:/home/jovyan/work" jupyter-starter-project:v1 /bin/bash
```

Then run poetry init and answer the questions to customise the toml file.

```cmd
poetry init
```

## Building and running the docker image in a single command with docker-compose

You can build and run the image using the command:
```cmd
docker-compose -f docker-compose.dev.yml up --build
```

Alternatively if you need to change the host port (e.g. because 8888 is in use) or change the image name you can use the following.  Note that you can include the HOST_PORT or IMAGE_NAME elements or both.

```cmd
set HOST_PORT=8888
set IMAGE_NAME=[NEW NAME HERE] && docker-compose -f docker-compose.dev.yml up --build
```

After either of these commands the log in the terminal will end in a message like this to let you know that your jupyter session is ready and available in the browser:

    Jupyter Server 2.15.0 is running at:
    http://localhost:8888/lab
        http://127.0.0.1:8888/lab


Click on the lowest link: http://127.0.0.1:8888/lab or cut and paste it into the browser.

Jupyter should then start running in the browser.

To create your first notebook go to File > New > Notebook.

## Shutting DOWN the container with docker-compose

```cmd
docker-compose -f docker-compose.dev.yml down
```

## Bringing back UP an image to container wihout a lengthy rebuild with docker-compose


```cmd
docker-compose -f docker-compose.dev.yml up
```


## Independently building and running the image

Rather than using docker-compose to combine tasks in a quick 'build and run' action, you can seperately build and the run the docker image.

### Independently building the Docker Image

To build the Docker image using the default Python version (Python 3.11):

First, choose a unique and descriptive name for the docker image that will be created and add a version number after a colon (e.g. jupyter-datasc-food:v1). Here we use oewg-work:latest.

Then run the following command in the terminal:
```bash
docker build -f Dockerfile.dev -t oewg-work:latest .
```

Note that in the Dockerfile.dev poetry is configured to install packages to the main system environment and not to a poetry env.
    poetry config virtualenvs.create false

### Independendently running the Docker image

To now run the docker image use the following command.

```bash
docker run -it --rm -p 8888:8888 -v "%cd%:/home/jovyan/work" oewg-pipeline:latest start-notebook.py --ServerApp.root_dir=/home/jovyan/work --NotebookApp.token=''
```

### Run commands in the container

The build command launches JupyterLab immediately and this occupies the terminal, but you can access the container and run commands by opening a new terminal and then running this (works in powershell): 

Replace CONTAINER_NUMBER with the long number associated with the container in Docker Desktop.

```bash
docker exec -it CONTAINER_NUMBER /bin/bash
```


## ToDo

1. Create a pre-commit script in the /git/hooks folder and use it pi-compile a requirements.txt every time I commit.  I have a lock.sh file that might help.

# A note on dependency management

There is a significant difference between Numpy 1.x and 2.x.  You build you package to depend on one of the other, but not both.

**Python 3.13 and Numpy 2**
Docling: YES. For Python >=3.13 uses Numpy >=2.1.0  (source: https://github.com/docling-project/docling-ibm-models/blob/7511f740bcb4d77e6934faaa17784d5b67236988/pyproject.toml#L27-L30)
Langchain: NO - check this. (see below) - but Langchain has a DoclingLoader now.
Spacy: NO. Latest version is 3.8.2 and that uses Python <3.13.
Jupyter Docker Stack: NO. Only has versions up to Python 3.12.

**Python 3.13 and Numpy 1**
Langchain: YES. For Python >=3.13 uses Numpy 1.x.  They are behind so hopefully will upgrade to Numpy 2.
Docling: NO. (see above)
Jupyter Docker Stack: NO. Only has versions up to Python 3.12.9
Spacy: NO. Latest version is 3.8.2 and that uses Python <3.13.

**Python 3.12 and Numpy 2**
Spacy: YES. Latest version is 3.8.4 and that uses Python <3.13 and numpy>=2.0.0,<3.0.0 and thinc = "8.3.3" (lock to this they suggest) (source: https://github.com/explosion/spaCy/issues/13528; source: https://github.com/explosion/spaCy/blob/master/requirements.txt)
Jupyter Docker Stack: YES. Has python 3.12.9. Could work with Numpy 2.x (but not checked this)
Docling: NO. Docling for Python <3.13 uses Numpy >=1.24.4,<2.0

**Python 3.12 and Numpy 1**
Docling: YES. Docling for Python <3.13 uses Numpy >=1.24.4,<2.0
Jupyter Docker YES: Has python 3.12.9. Could work with Numpy 1.x.
Spacy: 

(NB: Spacy community recommend Numpy 1.26.4 if wanting a Numpy 1.x)