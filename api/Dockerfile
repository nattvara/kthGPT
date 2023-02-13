FROM mcr.microsoft.com/playwright
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY api ./api
COPY config ./config
COPY db ./db
COPY jobs ./jobs
COPY tools ./tools
COPY setup.py .
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt
RUN python setup.py install
RUN playwright install
RUN playwright install-deps
