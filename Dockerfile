FROM python:3.6.5

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

RUN mkdir -p input

RUN mkdir -p output

COPY mining_nlp_repositories/ /app/mining_nlp_repositories/
