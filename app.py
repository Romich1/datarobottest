import requests
from flask import Flask, redirect, request
import os

github_auth_url = 'https://github.com/login/oauth/authorize'
github_api_url = 'https://api.github.com'
redirect_url = 'http://datarobottest.herokuapp.com/auth/redirect'
client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')
app = Flask('datarobottest')


@app.route('/')
@app.route('/index')
def index():
    return('It works!!')


@app.route('/auth')
def request_authorization():
    github_url_params = '%s?client_id=%s&redirect_uri=%s' % (github_auth_url, client_id, redirect_url)
    return redirect(github_url_params)


@app.route('/auth/redirect', methods=['POST'])
def redirect_auth():
    responce_code = requests.json.get('code')
    user_token = token_request(responce_code)
    return('Redirect auth triggered <br />  %s <br />  Token len %s' % (request.headers, len(user_token)) )


def token_request(token_code):
    token_url = 'https://github.com/login/oauth/access_token'
    parameters = {'client_id': client_id, 'client_secret': client_secret, 'code': token_code}
    r = requests.post(token_url, params=parameters)
    return r


if __name__ == '__main__':
    app.run()
