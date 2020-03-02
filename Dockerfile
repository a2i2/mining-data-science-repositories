FROM python:3.6.5

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

RUN mkdir -p input

RUN mkdir -p output

RUN apt-get update && apt-get install -y python-pip

RUN pip3 install virtualenv

RUN virtualenv -p python2 clean_env_py2

COPY requirements_venv_py2.txt /app

RUN /app/clean_env_py2/bin/pip2 install --trusted-host pypi.python.org -r requirements_venv_py2.txt

RUN virtualenv -p python3 clean_env_py3

COPY requirements_venv_py3.txt /app

RUN /app/clean_env_py3/bin/pip3 install --trusted-host pypi.python.org -r requirements_venv_py3.txt
