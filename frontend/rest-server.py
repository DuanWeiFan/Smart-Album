import grpc
import img_pb2
import img_pb2_grpc
import argparse
import pickle

class Rest_Server():
    def __init__(self, host):
        channel = grpc.insecure_channel('{}:50051'.format(host))
        self.stub = img_pb2_grpc.ImageProtoStub(channel)

    def send_image(self, img):
        # assume img to be bytes
        print('sending image')
        img_attribute = self.stub.ClassifyImage(img_pb2.ImageMsg(img=img))
        img_attribute = pickle.loads(img_attribute.msg)
        print('img attribute:', img_attribute)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    args=parser.parse_args()
    server = Rest_Server(args.host)
    img = open('../images/car.jpg', 'rb').read()
    server.send_image(img)
    
