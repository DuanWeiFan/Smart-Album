from __future__ import print_function
import requests
import json
import jsonpickle
import os
import argparse
import time
import urllib
import requests

class rest_client():
    def __init__(self, host):
        self.url = 'http://{}:5000'.format(host)

    def send_url_image(self, url):
        headers = {'content-type': 'image/{}'.format('jpg')}
        # img = urllib.request.urlopen(url).read()
        img = requests.get(url).content
        response = requests.put(
            self.url+'/image/classify/{}'.format('filename'),
            data=img, headers=headers)
        print(jsonpickle.decode(response.content))

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
    # client.send_image('../images/car.jpg')
    client.send_url_image('https://lh3.googleusercontent.com/lr/AGWb-e5GOcsgwdi9QjT50d1u0e_Brk8m9jn0HZLSOoNRVCYgX5K_Oup24n854u2JFmyXM-XgwMQ4QJ3cWi4irbXxa57s2Hz24JDy9QUtW-4vMTNRNtFN-fxAiZT9xUg5V7k-tZhBtsbO3zMZ6DxzuDOHLkxq9Vi3L_DsKW6pQ-aElMKFRngUZltopGSiEMv6Apzc24bUS_s3qAXJdopgp4WFbWwfUgCmy5jTaMKcizWuDrYwhplY5LGn_VoQZVZfEJila4u58VOpIklt4EjRqk3bozIBkSaDD6dWzgHiBlA8gyPQj4OIYgvzoN9IP_8PDTUftwIId4dpt5hSRiRysGY1jtAFz1B5_5LFvlNVbA2hJPNpYfg6118cEMJoX42NognwwalLQdmkPYnGREkQROjiSo-Hr4JqosXmsEMfQjVXVUcVgbHCFeJoDrX9aHgkCCBH0GdtuNjVsSiqMvRF7XlJy_Ds7dF5IxmkOL11U82q9pnStW14WhyA9Jti7V8w1MalIJQ2NR3PM1b9CjJkQBFQU-7Ma3mXiIkEMQmtX9LIPJM2pm0C9rGFMF6KTyd3d3G3ZEB7LGRdQZ7n-h7jjn_phkW8HZI_fiaOTnR_YYuRzfFR7yCBeTpM3e0C-ooNBWrYdTBkXqgKWAY2_CIHxkh4cg3dP2xaYSLpx42sZmmo5XuV5yn3a6s4DPqQX1D7fEhXTCKw8LqoDqNdElSneeRodaHQCsdqsEfYJJK7WPlZ_xk3ruhRDs3CitBrDls0syMf29iDEoQyNvJDuKkhnKBcKGa8ElzKbwJb70cuYa8T-j6TtQ')
