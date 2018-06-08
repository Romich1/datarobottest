# Self replication app

**Makes copy of own code to User`s Github account** 
 
 
**Usage scenario**

1) User goes by link 'Replicate app to my GitHub'
2) User redirects to GitHub authentication page and input own GitHub credential
3) After successful authentication user received status of replication (hopes successfully)


**Technical realization**

1) Provides web page with link that initiate app replication 
2) Makes request to authorization according to GitHub Oauth flow
https://developer.github.com/apps/building-oauth-apps/authorizing-oauth-apps/
3) With received users token - creates new repo and writes applications files into it


**Setup**

For run app on your server:
1) Define address where app will be hosted ( _yourappdomain.com_ for example)
2) Register app in your GitHub account 
3) Receive `client_id` and `client_secret` from gitHub for this app
4) Set `redirect_uri` in application setting on GitHub in format _yourappdomain.com**/replicate/redirect**_ 
    (just add  _**/replicate/redirect**_ to your hosting address)      
5) Set `client_id` and `client_secret` environment variables received on step 3 
    (way how to set environment variables depends on your hosting solution) 
6) Run application on your hosting  

If everything run fine you should observe app index page at your hosting address 


**Heroku settings files** 

For deployment to Heroku you can use predefined settings files - `Procfile` and `runtime.txt` 