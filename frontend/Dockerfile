FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install -U Flask pillow jsonpickle redis pika
RUN pip3 install grpcio protobuf
RUN pip3 install numpy redis
COPY rest-server.py .
COPY img_pb2_grpc.py .
COPY img_pb2.py .
ENTRYPOINT [ "python3", "rest-server.py", "image-worker", "redis" ]
