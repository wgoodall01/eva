FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update 
RUN apt-get install -y \
  build-essential \
  wget \
  git \
  python3 \
  python3-venv \
  python3-pip \
  openjdk-11-jdk-headless \
  ffmpeg \
  libsm6 \
  libxext6

RUN pip3 install venv-run

WORKDIR /eva

# Set up virtualenv
COPY ./pyproject.toml setup.py README.md /eva/
COPY ./eva/version.py /eva/eva/version.py
RUN rm -rf venv \
  && python3 -m venv venv \
  && venv-run pip install --upgrade pip \
  && venv-run pip install -e ".[dev]"


# Generate the parser
COPY ./script /eva/script
COPY ./eva/parser /eva/eva/parser
RUN ./script/antlr4/generate_parser.sh

# Run the test suite
COPY . /eva/
RUN PYTHONPATH="./" venv-run pytest test/ -s -v --log-level=WARNING

