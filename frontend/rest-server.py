import grpc
import img_pb2
import img_pb2_grpc
import argparse
import pickle
import hashlib
import jsonpickle
import io
from PIL import Image
from flask import Flask, request, Response

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
        return img_attribute

    def run(self):
        app = Flask(__name__)

        @app.route('/image/classify/<filename>', methods=['PUT'])
        def put_image(filename):
            r = request
            # convert the data to a PIL image type so we can extract dimensions
            ioBuffer = io.BytesIO(r.data)
            md5 = hashlib.md5(ioBuffer.getvalue()).hexdigest()
            image_data = {
                'image': r.data,
                'md5': md5,
                'filename': filename
            }
            img_attribute = self.send_image(pickle.dumps(image_data))
            return Response(
                response=jsonpickle.encode(img_attribute),
                status=200,
                mimetype="application/json"
            )
        app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    args=parser.parse_args()
    server = Rest_Server(args.host)
    server.run()
    # img = open('../images/car.jpg', 'rb').read()
    # server.send_image(img)
    
