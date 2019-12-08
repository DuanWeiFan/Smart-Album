import grpc
import img_pb2
import img_pb2_grpc
import argparse
import pickle
import hashlib
import jsonpickle
import io
import os
import redis
import requests
from PIL import Image
from flask import Flask, request, Response, render_template
import flask
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from base64 import b64encode

class Rest_Server():
    def __init__(self, worker_host, redis_host):
        channel = grpc.insecure_channel('{}:50051'.format(worker_host))
        self.stub = img_pb2_grpc.ImageProtoStub(channel)
        self.redisByImage = redis.Redis(host=redis_host, db=1, decode_responses=True)
        self.redisByClass = redis.Redis(host=redis_host, db=2, decode_responses=True)
        self.init_auth()

    def init_auth(self):
        self.CLIENT_SECRETS_FILE = "auth/client_secret.json"
        self.SCOPES = ['https://www.googleapis.com/auth/photoslibrary']
        self.API_SERVICE_NAME = 'photoslibrary'
        self.API_VERSION = 'v1'

    def send_image(self, img):
        # assume img to be bytes
        print('sending image')
        img_attribute = self.stub.ClassifyImage(img_pb2.ImageMsg(img=img))
        img_attribute = pickle.loads(img_attribute.msg)
        print('img attribute:', img_attribute)
        return img_attribute

    def process_google_photos(self, app, photo_dic):
        for photo in photo_dic:
            img_url = photo_dic[photo]
            # drop duplicate photos
            if not self.redisByImage.get(img_url):
                try:
                    img_content = requests.get(img_url).content
                    img_attribute = self.send_image(img_content)
                    self.save_img_to_redis(img_url, img_attribute)
                except Exception as e:
                    app.logger.debug('Exception: %s, url: %s', e, img_url)
        app.logger.info('Done Processing Google Photos')

    def save_img_to_redis(self, filename, img_attribute):
        if img_attribute['confidence'] > 0.5:
            self.redisByImage.set(filename, img_attribute['class'])
            self.redisByClass.rpush(img_attribute['class'], filename)
        else:
            self.redisByImage.set(filename, 'others')
            self.redisByClass.rpush('others', filename)

    def credentials_to_dict(self, credentials):
        return {'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes}
    
    def images_url_to_images_b64(self, images_url):
        images = []
        for img_url in images_url:
            img_content = requests.get(img_url).content
            img = b64encode(img_content).decode('utf-8')
            images.append(img)
        return images

    def search_images_by_class(self, search_term):
        images_url = []
        img_classes = []
        if self.redisByClass.lrange(search_term, 0, -1):
            images_url = self.redisByClass.lrange(search_term, 0, -1)
            img_classes = [search_term for _ in range(len(images_url))]
        return self.images_url_to_images_b64(images_url), img_classes
    
    def get_all_images(self):
        images_url = []
        img_classes = []
        for img_url in self.redisByImage.scan_iter('*'):
            images_url.append(img_url)
        for img_url in images_url:
            img_classes.append(self.redisByImage.get(img_url))
        return self.images_url_to_images_b64(images_url), img_classes
        

    def images_to_images_2d(self, images: list):
        images_2d = [[]]
        for i in range(len(images)):
            if len(images_2d[-1]) == 3:
                images_2d.append([])
            images_2d[-1].append(images[i])
        return images_2d

    def create_html_code_from_images(self, images: list, img_classes: list):
        print('num of images:', len(images))
        images_2d = self.images_to_images_2d(images)
        html_code = ''
        idx = 0
        for img3 in images_2d:
            html_code += '''<div class="w3-third">'''
            for img in img3:
                html_code += '''<img src="data:;base64,{}" style="width:100%" onclick="onClick(this)" alt="image class: {}"> '''.format(img, img_classes[idx])
                idx += 1
            html_code += '''</div>'''
        return html_code

    def run(self):
        app = Flask(__name__)

        @app.route('/')
        def login():
            return render_template('login.html')

        @app.route('/authorize')
        def authorize():
            # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                self.CLIENT_SECRETS_FILE, scopes=self.SCOPES)

            # The URI created here must exactly match one of the authorized redirect URIs
            # for the OAuth 2.0 client, which you configured in the API Console. If this
            # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
            # error.
            flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

            authorization_url, state = flow.authorization_url(
                # Enable offline access so that you can refresh an access token without
                # re-prompting the user for permission. Recommended for web server apps.
                access_type='offline',
                # Enable incremental authorization. Recommended as a best practice.
                include_granted_scopes='false')

            # Store the state so the callback can verify the auth server response.
            flask.session['state'] = state

            return flask.redirect(authorization_url)

        @app.route('/oauth2callback')
        def oauth2callback():
            # Specify the state when creating the flow in the callback so that it can
            # verified in the authorization server response.
            state = flask.session['state']

            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                self.CLIENT_SECRETS_FILE, scopes=self.SCOPES, state=state)
            flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

            # Use the authorization server's response to fetch the OAuth 2.0 tokens.
            authorization_response = flask.request.url
            flow.fetch_token(authorization_response=authorization_response)

            # Store credentials in the session.
            # ACTION ITEM: In a production app, you likely want to save these
            #              credentials in a persistent database instead.
            credentials = flow.credentials
            flask.session['credentials'] = self.credentials_to_dict(credentials)

            return flask.redirect(flask.url_for('process_images'))

        @app.route('/process_images')
        def process_images():
            # Load credentials from the session.
            credentials = google.oauth2.credentials.Credentials(
                **flask.session['credentials'])

            # build the service
            google_photos = googleapiclient.discovery.build(
                self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials)

            nextpagetoken = 'Dummy'
            while nextpagetoken != '':
                nextpagetoken = '' if nextpagetoken == 'Dummy' else nextpagetoken
                results = google_photos.mediaItems().list().execute()
                files = results
                # The default number of media items to return at a time is 25. The maximum pageSize is 100.
                items = results.get('mediaItems', [])
                nextpagetoken = results.get('nextPageToken', '')
                url_list = []
                dic = {}
                for item in items:
                        dic[item['id']] = item['baseUrl']

            # Save credentials back to session in case access token was refreshed.
            # ACTION ITEM: In a production app, you likely want to save these
            #              credentials in a persistent database instead.
            flask.session['credentials'] = self.credentials_to_dict(credentials)
            app.logger.info('Start processing google photos')
            self.process_google_photos(app, dic)
            self.photo_dic = dic
            app.logger.info('Done processing! Number of photos: %s', len(dic))
            return flask.redirect('index')

        @app.route('/index', methods=['GET', 'POST'])
        def index():
            # return "Hello, Welcome to Data-Center Project"
            if 'credentials' not in flask.session:
                return flask.redirect('authorize')
    
            if request.method == 'POST':
                search_term = request.form.get('searchTerm')
                images, img_classes = self.search_images_by_class(search_term)
                html_code = self.create_html_code_from_images(images, img_classes)
                app.logger.info('%s of photos', len(images))
                return render_template('index2.html', portfolio=html_code, images=images, len=len(images))
            images, img_classes = self.get_all_images()
            app.logger.info('%s of photos', len(images))
            html_code = self.create_html_code_from_images(images, img_classes)
            return render_template('index2.html', portfolio=html_code, images=[], len=0)

        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        app.secret_key = '~"K_\xef\xec\xb3L\x002\x9e:\xbd\x19\xe9\xeeY)\xf7\x92j\x06|W'
        app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('worker', type=str)
    parser.add_argument('redis', type=str)
    args=parser.parse_args()
    server = Rest_Server(args.worker, args.redis)
    server.run()
