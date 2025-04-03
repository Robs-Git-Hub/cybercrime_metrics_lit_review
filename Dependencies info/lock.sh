#!/bin/sh
set -eux

# Define the base image (must match the one in your Dockerfile)
base_image=quay.io/jupyter/minimal-notebook:2025-03-12

# Run a container from the base image to generate a constraints file
docker run --rm -v $PWD:/io -w /io $base_image sh -c "
    pip list --format=freeze > base-env.txt
    pip install pip-tools
    pip-compile -c base-env.txt -r requirements.in
"
