from flask import Flask, url_for, render_template, request, flash, jsonify, session
from flask_oauthlib.client import OAuth
from markupsafe import Markup
import os
import json
import pymongo
import sys
import pprint
app = Flask(__name__) #__name__ = "__main__" if this is the file that was run.  Otherwise, it is the name of the file (ex. webapp)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key = os.environ['SECRET_KEY']
oauth = OAuth(app)
oauth.init_app(app)

github = oauth.remote_app(
    'github',
    consumer_key=os.environ['GITHUB_CLIENT_ID'], #your web app's "username" for github's OAuth
    consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],#your web app's "password" for github's OAuth
    request_token_params={'scope': 'user:email'}, #request read-only access to the user's email.  For a list of possible scopes, see developer.github.com/apps/building-oauth-apps/scopes-for-oauth-apps
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',  
    authorize_url='https://github.com/login/oauth/authorize' #URL for github's OAuth login
)

@app.context_processor
def inject_logged_in():
    is_logged_in = 'github_token' in session #this will be true if the token is in the session and false otherwise
    return {"logged_in":is_logged_in}
    
@app.route('/login')
def login():   
    return github.authorize(callback=url_for('authorized', _external=True, _scheme='http'))
    
@app.route('/logout')
def logout():
    session.clear()
    return render_template('home.html', message='You were logged out')
    
@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        session.clear()
        message = 'Access denied: reason=' + request.args['error'] + ' error=' + request.args['error_description'] + ' full=' + pprint.pformat(request.args)      
    else:
        try:
            session['github_token'] = (resp['access_token'], '') #save the token to prove that the user logged in
             session['user_data']=github.get('user').data
            #pprint.pprint(vars(github['/email']))
           # pprint.pprint(vars(github['api/2/accounts/profile/']))
            message='You were successfully logged in as ' + session['user_data']['login'] + '.'
        except Exception as inst:
            session.clear()
            print(inst)
            message='Unable to login, please try again.  '
    return render_template('home.html', message=message)

@github.tokengetter
def get_github_oauth_token():
    return session['github_token']
    
@app.route("/")
def render_home():
   return render_template('home.html')


if __name__=="__main__":
    app.run(debug=True)