#import json
#import oauth2
import requests
from flask import Flask, session, request

app = Flask('flask_name')
callbackurl = 'http://murmuring-tundra-47748.herokuapp.com/callback'
redirecturl = 'http://murmuring-tundra-47748.herokuapp.com/redirect'
gitapi = 'https://api.github.com'

@app.route('/')
def root():
    return('It works!!')

@app.route('/auth')
def request_authorization():
    print('request_authorization')
    r = authorize()
    return(r)

@app.route('/response')
def handle_responce():
    return('Response recieved')

@app.route('/callback')
def callback():
    return('callback triggered \n %s' % request.headers)

@app.route('/redirect')
def redirect():
    return('Redirect triggered \n %s' % request.headers)

def authorize():
    github_url = 'https://github.com/login/oauth/authorize'
    params = {'client_id': 'f7d95f0c925ee3c42ed9 ', 'url': redirecturl}
    print(params)
    r = requests.get(github_url)
    return r

app.run()