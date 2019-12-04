FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install -U Flask pillow jsonpickle redis pika
RUN pip3 install grpcio protobuf
RUN pip3 install numpy redis
RUN pip3 install google-oauth google-auth-oauthlib google-api-python-client google-auth-httplib2
WORKDIR /user/local/frontend
COPY . ./
ENTRYPOINT [ "python3", "rest-server.py", "image-worker", "redis" ]
