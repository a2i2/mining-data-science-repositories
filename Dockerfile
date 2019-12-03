FROM python:3.6.5


WORKDIR /app

COPY requirements.txt /app

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt


COPY . /app

CMD ["python3", "./mining_nlp_repositories/task_explore.py"]
