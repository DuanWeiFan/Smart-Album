python3 -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. ./img.proto

cp img_pb2_grpc.py ./worker
cp img_pb2.py ./worker

mv img_pb2_grpc.py ./frontend
mv img_pb2.py ./frontend