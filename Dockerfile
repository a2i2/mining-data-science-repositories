FROM python:3.6.5

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

RUN mkdir -p input

RUN mkdir -p output

RUN apt-get update && apt-get install -y python-pip

COPY requirements_py2.txt /app

RUN pip2 install --trusted-host pypi.python.org -r requirements_py2.txt

#COPY mining_nlp_repositories/ /app/mining_nlp_repositories/
