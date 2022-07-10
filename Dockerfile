# pull official base image
FROM python:3.10.1-slim-buster

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# install system dependencies
RUN  apt-get update \
  && apt-get -y install netcat gcc \
  && apt-get clean

# Make sure this matches what's in the pyproject.toml file
ENV POETRY_VERSION 1.0.0

# install Poetry
RUN pip install poetry==$POETRY_VERSION

# install python dependencies
COPY poetry.lock pyproject.toml ./

# Perform install
RUN poetry config virtualenvs.create false
RUN poetry install $(test "$ENVIRONMENT" = production && echo "--no-dev")


# add app
COPY . ./
