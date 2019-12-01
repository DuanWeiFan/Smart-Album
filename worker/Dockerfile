FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install tensorflow keras grpcio
COPY worker.py .
COPY img_pb2.py .
COPY img_pb2_grpc.py .
ENTRYPOINT [ "python3", "worker.py" ]
