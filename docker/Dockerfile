FROM centos:latest

RUN yum -y install epel-release && \
    yum clean all && \
    yum -y install python-pip make

RUN pip install --upgrade pip

COPY docker/requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /data

CMD ["/bin/bash"]
