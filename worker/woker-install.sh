apt-get update
apt-get install -y python3 python3-pip
pip3 install tensorflow keras grpcio
pip3 install Pillow

curl http://metadata/computeMetadata/v1/instance/attributes/worker -H "Metadata-Flavor: Google" > worker.py
curl http://metadata/computeMetadata/v1/instance/attributes/img_pb2_grpc -H "Metadata-Flavor: Google" > img_pb2_grpc.py
curl http://metadata/computeMetadata/v1/instance/attributes/img_pb2 -H "Metadata-Flavor: Google" > img_pb2.py
python3 worker.py &
