from base64 import b64encode
from flask import Flask, redirect, request, jsonify
import requests
import os

github_auth_url = 'https://github.com/login/oauth/authorize'
github_api_url = 'https://api.github.com'
redirect_url = 'http://datarobottest.herokuapp.com/auth/redirect'
client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')
#git_token = os.environ.get('git_token') #for local debug
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
    #response_r = replicate_app(git_token) #for local debug
    #return 'Success: %s <br /> error message: %s' % (response_r.get('result'), response_r.get('error_message')) #for local debug
    response_code = request.values.get('code')
    token_response = token_request(response_code)
    try:
        user_token = token_response.json().get('access_token')
    except ValueError:
        user_token = None
    if user_token is None:
        return('Token recieving error <br /> Response headers <br />  %s <br /> Response text <br /> %s ' % (token_response.headers,jsonify(token_response.text)))
    return replicate_app(user_token)


def token_request(token_code):
    token_url = 'https://github.com/login/oauth/access_token'
    parameters = {'client_id': client_id, 'client_secret': client_secret, 'code': token_code}
    headers = {'Accept': 'application/json'}
    response = requests.post(token_url, params=parameters, headers=headers)
    return response


def create_repo(token, user_name, repo_name):
    url = 'https://api.github.com/user/repos'
    url_get = 'https://api.github.com/repos/%s/%s' % (user_name,repo_name)
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer %s' % token}
    description = 'Makes own copy to users repo'
    parameters = {'name': repo_name, 'description': description}

    response_get = requests.get(url_get, headers=headers, json=parameters)
    if response_get.status_code == 200:
        return {'result': False, 'error_message': 'repo %s already exist' % repo_name}
    response_post = requests.post(url, headers=headers, json=parameters)

    if response_post.status_code == 201:
        return {'result': True, 'error_message': ''}
    else:
        return {'result': False, 'error_message': response_post.text}


def write_file_to_repo(token,  user_name, repo_name, file):
    try:
        with open(file, mode='rb') as data_file:
            file_content = b64encode(data_file.read()).decode("utf-8")
    except IOError:
        return {'result':False, 'error_message':'file reading error'}

    url = 'https://api.github.com/repos/%s/%s/contents/%s' % (user_name, repo_name, str(file))
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer %s' % token}
    parameters = {'path': str(file), 'message': 'piu', 'content': file_content}
    response_put = requests.put(url, headers=headers, json=parameters)

    if response_put.status_code == 201:
        return {'result':True, 'error_message':''}
    else:
        return {'result':False, 'error_message':response_put.text}


def user_info(token):
    url = 'https://api.github.com/user'
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer %s' % token}
    response_get = requests.get(url, headers=headers)
    if response_get.status_code != 200:
        return {'result': False, 'error_message': response_get.text}
    else:
        return {'result': True, 'error_message': '', "user_info":response_get.json()}


def replicate_app(token):
    result = {'result': True, 'error_message': ''}

    response_ui = user_info(token)
    if not response_ui.get('result'):
        result['result'] = False
        result['error_message'] += '\n Getting user info error- %s' % response_ui.get('error_message')
        return result
    user_name = response_ui.get('user_info').get('login')

    repo_name = 'self_replicated_app'
    response_cr = create_repo(token, user_name, repo_name)
    if not response_cr.get('result'):
        result['result'] = False
        result['error_message'] += '\n Repo %s creating error - %s' % (repo_name, response_cr.get('error_message'))
        return result

    for file in os.listdir('.'):
        if file[0] == '.':
            continue
        response_wfr = write_file_to_repo(token, user_name, repo_name, file)
        if not response_wfr.get('result'):
            result['result'] = False
            result['error_message'] += '\n File %s creating error - %s' % (str(file), response_wfr.get('error_message'))

    return result

if __name__ == '__main__':
    app.run()