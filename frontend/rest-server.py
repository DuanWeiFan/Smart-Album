import grpc
import img_pb2
import img_pb2_grpc
import argparse
import pickle
import hashlib
import jsonpickle
import io
import redis
from PIL import Image
from flask import Flask, request, Response

class Rest_Server():
    def __init__(self, worker_host, redis_host):
        channel = grpc.insecure_channel('{}:50051'.format(worker_host))
        self.stub = img_pb2_grpc.ImageProtoStub(channel)
        self.redisByImage = redis.Redis(host=redis_host, db=1, decode_responses=True)
        self.redisByClass = redis.Redis(host=redis_host, db=2, decode_responses=True)

    def send_image(self, img):
        # assume img to be bytes
        print('sending image')
        img_attribute = self.stub.ClassifyImage(img_pb2.ImageMsg(img=img))
        img_attribute = pickle.loads(img_attribute.msg)
        print('img attribute:', img_attribute)
        return img_attribute

    def run(self):
        app = Flask(__name__)

        @app.route('/', methods=['GET'])
        def hello():
            return "Hello, Welcome to Data-Center Project"

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
            if img_attribute['confidence'] > 0.5:
                self.redisByImage.set(filename, img_attribute['class'])
                self.redisByClass.rpush(img_attribute['class'], filename)
            else:
                self.redisByImage.set(filename, 'others')
                self.redisByClass.rpush('others', filename)
            return Response(
                response=jsonpickle.encode(img_attribute),
                status=200,
                mimetype="application/json"
            )
        @app.route('/image/class/<class_name>', methods=['GET'])
        def get_image_by_class(class_name):
            images = []
            if self.redisByClass.lrange(class_name, 0, -1):
                images = self.redisByClass.lrange(class_name, 0, -1)
            response = {
                'images': images
            }
            response_pickled = jsonpickle.encode(response)
            return Response(response=response_pickled,
                            status=200,
                            mimetype="application/json")
        @app.route('/image/filename/<filename>', methods=['GET'])
        def get_class_by_filename(filename):
            class_name = None
            if self.redisByImage.get(filename):
                class_name = self.redisByImage.get(filename)
            response = {
                'class_name': class_name
            }
            response_pickled = jsonpickle.encode(response)
            return Response(response=response_pickled,
                            status=200,
                            mimetype="application/json")
        app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('worker', type=str)
    parser.add_argument('redis', type=str)
    args=parser.parse_args()
    server = Rest_Server(args.worker, args.redis)
    server.run()
    # img = open('../images/car.jpg', 'rb').read()
    # server.send_image(img)
    
