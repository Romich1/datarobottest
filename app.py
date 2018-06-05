import requests
from flask import Flask, redirect, request
import os

callbackurl = 'http://datarobottest.herokuapp.com/callback'
redirecturl = 'http://datarobottest.herokuapp.com/auth/redirect'
github_auth_url = 'https://github.com/login/oauth/authorize'
github_api_url = 'https://api.github.com'
client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')
app = Flask('flask_name')


@app.route('/')
@app.route('/index')
def index():
    return('It works!!')


@app.route('/auth')
def request_authorization():
    return authorize()
    #return(r.text)


@app.route('/response')
def handle_responce():
    return('Response recieved')


@app.route('/callback')
def callback():
    return('callback triggered \n %s' % request.headers)


@app.route('/redirect/auth/', methods=['POST'])
def redirect_auth():
    token_request(request.values.get('authenticity_token'))
    return('Redirect auth triggered <br />  %s <br />  %s' % (request.headers, requests.json) )


@app.route('/session', methods=['POST'])
def session():
    token_request(request.values.get('authenticity_token'))
    return('session triggered <br /> <br /> %s <br /> <br />  %s' % (request.headers, request.values) )


def authorize():

    github_url_params = '%s?client_id=%s&redirect_uri=%s' % (github_auth_url, client_id, redirecturl)
    #parameters = {'client_id': client_id, 'redirect_uri': redirecturl}
    #r = requests.get(github_url, params=parameters))
    return redirect(github_url_params)


def token_request(token_code):
    token_url = 'https://github.com/login/oauth/access_token'
    parameters = {'client_id': client_id, 'client_secret': client_secret, 'code': token_code}
    r = requests.post(token_url, params=parameters)
    print(r.text)


if __name__ == '__main__':
    app.run()
