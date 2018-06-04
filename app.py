#import oauth2
import requests
from flask import Flask, session, request

callbackurl = 'http://datarobottest.herokuapp.com/callback'
redirecturl = 'http://datarobottest.herokuapp.com/redirect'
gitapi = 'https://api.github.com'
app = Flask('flask_name')

@app.route('/')
@app.route('/index')
def index():
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
    parameters = {'client_id': 'f7d95f0c925ee3c42ed9', 'url': redirecturl}
    r = requests.get(github_url, params = parameters)
    return r

if __name__ == '__main__':
    app.run()
