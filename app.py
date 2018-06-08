"""
Application that replicate itself to user`s github
Usage scenario:
1) User goes by link 'Replicate app to my GitHub'
2) User redirects to GitHub authentication page and input own GitHub credential
3) After successful authentication user received status of replication (hopes successfully)

Technically uses next realization:
1) Provide link for user to replicate app
2) Make authorization according to gitHub Oauth logic
https://developer.github.com/apps/building-oauth-apps/authorizing-oauth-apps/
3) With received users token - create new repo and write applications files into it
"""

from base64 import b64encode
from flask import Flask, redirect, request, jsonify
import requests
import os

local_debug = False  # local debugging with existed token (expected in 'git_token' env variable)
github_auth_url = 'https://github.com/login/oauth/authorize'
github_api_url = 'https://api.github.com'
redirect_url = 'https://datarobottest.herokuapp.com/replicate/redirect'  # should be the same as 'redirect Irl' in gitHub for this app
scope = 'public_repo'
client_id = os.environ.get('client_id')  # provided by gitHub for this app
client_secret = os.environ.get('client_secret')  # provided by gitHub for this app
if local_debug:  # local debugging with existed token
    git_token = os.environ.get('git_token')
app_files = ('app.py', 'README.md', 'requirements.txt')  # app`s files that will be replicated!
heroku_files = ('Procfile', 'Procfile.Windows', 'runtime.txt')  # files for deployment to Heroku
app = Flask('datarobottest')


@app.route('/')
@app.route('/index')
def index():
    """Main page"""
    replicate_link = '<a href="/replicate">Replicate app to your GitHub</a>'
    return('Self replicated app description <br/> <br/> %s <br/>(Needs your GitHub credential)' % replicate_link)


@app.route('/replicate')
def request_authorization():
    """Initiates app replication"""
    if local_debug:
        response_r = replicate_app(git_token)
        return 'Success: %s <br /> error message: %s' % (response_r.get('result'), response_r.get('error_message'))

    github_url_params = '%s?client_id=%s&redirect_uri=%s&scope=%s' % (github_auth_url, client_id, redirect_url, scope)
    return redirect(github_url_params)


@app.route('/replicate/redirect')
def redirect_auth():
    """Handles income callback from GitHub after authentication"""
    response_code = request.values.get('code')
    token_response = token_request(response_code)
    try:
        user_token = token_response.json().get('access_token')
    except ValueError:
        user_token = None
    if user_token is None:
        return('Token recieving error <br /> Response headers <br />  %s <br /> Response text <br /> %s ' % (token_response.headers,jsonify(token_response.text)))

    response_ra = replicate_app(user_token)
    return 'Success: %s <br /> error message: %s' % (response_ra.get('result'), response_ra.get('error_message'))


def token_request(token_code):
    """Requests users token with received 'code' parameter"""
    token_url = 'https://github.com/login/oauth/access_token'
    parameters = {'client_id': client_id, 'client_secret': client_secret, 'code': token_code}
    headers = {'Accept': 'application/json'}
    response = requests.post(token_url, params=parameters, headers=headers)
    return response


def create_repo(token, user_name, repo_name):
    """Creates new repo in user`s account
    Checks if repo name exist and returns error if exist
    """
    url = 'https://api.github.com/user/repos'
    url_get = 'https://api.github.com/repos/%s/%s' % (user_name, repo_name)
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
    """Writes app files to user`s repo
    Files list to write receives in app_files variable
    Does not check if file exist! Always writes to new repo. Should be fixed with re-write logic (not developed yet)
    """
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
    """Receives user info by token. Uses for getting user name"""
    url = 'https://api.github.com/user'
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer %s' % token}
    response_get = requests.get(url, headers=headers)
    if response_get.status_code != 200:
        return {'result': False, 'error_message': response_get.text}
    else:
        return {'result': True, 'error_message': '', "user_info":response_get.json()}


def replicate_app(token):
    """Main function
    Creates new repo and writes files into it
    Return result dict with structure ('result','error_message')
    Error messages accumulates if were several errors
    """
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

    for file in (app_files + heroku_files):
        response_wfr = write_file_to_repo(token, user_name, repo_name, file)
        if not response_wfr.get('result'):
            result['result'] = False
            result['error_message'] += '\n File %s creating error - %s' % (str(file), response_wfr.get('error_message'))

    return result


if __name__ == '__main__':
    app.run()
