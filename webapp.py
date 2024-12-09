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

connection_string = os.environ["MONGO_CONNECTION_STRING"]
db_name = os.environ["MONGO_DBNAME"]
    
client = pymongo.MongoClient(connection_string)
db = client[db_name]
collection = db['ForumCL'] #1. put the name of your collection in the quotes

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
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
    PostData = ""
    documents = []
    for c in collection.find():
        PostData = PostData + Markup("<div class='card'>\n\t<div class='card-header'>"+c["User"]+"</div>\n\t<div class='card-body'>"+c["Message"]+"</div>\n</div>\n")
        documents.append({"User": c["User"], "Message": c["Message"]})
    return render_template('home.html', message='You were logged out', PostData=PostData, documents=documents)
    
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
    PostData = ""
    documents = []
    for c in collection.find():
        PostData = PostData + Markup("<div class='card'>\n\t<div class='card-header'>"+c["User"]+"</div>\n\t<div class='card-body'>"+c["Message"]+"</div>\n</div>\n")
        documents.append({"User": c["User"], "Message": c["Message"]})
    return render_template('home.html', message=message, PostData=PostData, documents=documents)

@github.tokengetter
def get_github_oauth_token():
    return session['github_token']
    
@app.route("/", methods=['GET','POST'])
def render_home():
    PostData = ""
    documents = []

    if "post" in request.form:
        newDict = {"User":session['user_data']['login'],"Message": request.form["post"]} 
        LastDoc = {}
        for doc in collection.find():
            LastDoc = doc
        print(newDict)
        print(LastDoc)
        if newDict["User"] != LastDoc["User"] or newDict["Message"] != LastDoc["Message"]:
            collection.insert_one(newDict)
            #PostData = PostData + Markup("<div class='card'>\n\t<div class='card-header'>"+c["User"]+"</div>\n\t<div class='card-body'>"+c["Message"]+"</div>\n</div>\n")
            print(request.form["post"])
         
        
        
    for c in collection.find():
        PostData = PostData + Markup("<div class='card'>\n\t<div class='card-header'>"+c["User"]+"</div>\n\t<div class='card-body'>"+c["Message"]+"</div>\n</div>\n")
        documents.append({"User": c["User"], "Message": c["Message"]})
    
    return render_template('home.html', PostData=PostData, documents=documents)

if __name__=="__main__":
    app.run(debug=True)