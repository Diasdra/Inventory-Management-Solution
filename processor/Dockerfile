FROM ubuntu:20.04

LABEL maintainer="jwu356@bcit.ca"

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /processor/requirements.txt

WORKDIR /processor

RUN pip3 install -r requirements.txt
COPY . /processor
RUN python3 create_table.py

ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]