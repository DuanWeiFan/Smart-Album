from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import decode_predictions
from keras.applications.vgg16 import VGG16
from concurrent import futures
from PIL import Image
import img_pb2
import img_pb2_grpc
import grpc
import keras
import io
import pickle

class Worker_Server(img_pb2_grpc.ImageProtoServicer):
    def __init__(self):
        self.init_model()
        self.VGG_IMG_SIZE = (224,224)

    def init_model(self):
        self.model = VGG16()

    def predict(self, img: Image):
        img = img.resize(self.VGG_IMG_SIZE)
        img = img_to_array(img)
        img = img.reshape((1, img.shape[0], img.shape[1], img.shape[2]))
        img = preprocess_input(img)
        prediction = decode_predictions(self.model.predict(img))[0][0]
        print('prediction:', prediction)
        msg = {
            'class': prediction[1],
            'confidence': prediction[2]
        }
        return msg

    def ClassifyImage(self, request, context):
        img_data = pickle.loads(request.img)
        ioBuffer = io.BytesIO(img_data['image'])
        img = Image.open(ioBuffer)
        classification = self.predict(img)
        return img_pb2.ImageAttribute(msg=pickle.dumps(classification))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
    img_pb2_grpc.add_ImageProtoServicer_to_server(Worker_Server(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    # print('testing worker')
    # worker = worker_server()
    # img = open('images/car.jpg', 'rb').read()
    # img = Image.open(io.BytesIO(img))
    # worker.predict(img)
    print('start serving')
    serve()
