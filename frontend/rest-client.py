from __future__ import print_function
import requests
import json
import jsonpickle
import os
import argparse
import time

class rest_client():
    def __init__(self, host):
        self.url = 'http://{}:5000'.format(host)

    def send_image(self, img_path):
        filename = os.path.basename(img_path).split('.')[0]
        start_time = time.perf_counter()
        fields = img_path.split('.')
        img_type = fields[-1]
        headers = {'content-type': 'image/{}'.format(img_type)}
        img = open('{}'.format(img_path), 'rb').read()
        response = requests.put(
            self.url+'/image/classify/{}'.format(filename),
            data=img, headers=headers)
        end_time = time.perf_counter()
        print('cost time:', end_time - start_time)
        print(jsonpickle.decode(response.content))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    args = parser.parse_args()

    client = rest_client(args.host)
    client.send_image('../images/car.jpg')
