
FROM ubuntu:latest
RUN mkdir /data
RUN apt-get update
RUN apt install -y ansible python python-pip
COPY docker/requirements.txt .
RUN pip install -r requirements.txt
