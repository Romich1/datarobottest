import json
from flask import Flask, redirect, request, jsonify
import requests
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


@app.route('/auth/redirect', methods=['GET', 'POST'])
def redirect_auth():
    responce_code = request.values.get('code')
    token_responce = token_request(responce_code)
    try:
        user_token = token_responce.json().get('access_token')
    except ValueError:
        user_token = None

    if user_token is None:
        return('Token recieving error <br /> Headers <br />  %s <br /> Responce text <br /> %s ' % (token_responce.headers,jsonify(token_responce.text)))
    else:
        return users_repos(user_token)


def token_request(token_code):
    token_url = 'https://github.com/login/oauth/access_token'
    parameters = {'client_id': client_id, 'client_secret': client_secret, 'code': token_code}
    headers = {'Accept': 'application/json'}
    response = requests.post(token_url, params=parameters, headers=headers)
    return response

def users_repos(token):
    url = 'https://api.github.com/user/repos'
    headers = {'Accept': 'application/json','Authorization':'Bearer %s' %token}
    response = requests.post(url, headers=headers)
    return jsonify(response.text)

if __name__ == '__main__':
    app.run()
