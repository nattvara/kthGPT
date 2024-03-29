FROM ubuntu:22.04

# Prevent dialog prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Install system tools, Python, FastAPI essentials, and Playwright's dependencies
RUN apt-get update && apt-get install -y \
    wget \
    python3-pip \
    python3-venv \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libnss3 \
    libpq-dev \
    libxss1 \
    libasound2 \
    build-essential \
    rustc \
    cargo \
    ffmpeg \
    gunicorn \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# copy project
COPY api ./api
COPY config ./config
COPY db ./db
COPY jobs ./jobs
COPY tools ./tools
COPY courses ./courses
COPY classifiers ./classifiers
COPY index ./index
COPY setup.py .
COPY requirements.txt .

# install pyhton dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# install playwright and dependencies
RUN python3 setup.py install
RUN playwright install
RUN playwright install-deps
