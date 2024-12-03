from flask import Flask, url_for, render_template, request, flash
from markupsafe import Markup
import os
import json
import pymongo
import sys
import pprint
app = Flask(__name__) #__name__ = "__main__" if this is the file that was run.  Otherwise, it is the name of the file (ex. webapp)

@app.route("/")
def render_home():
   # connection_string = os.environ["MONGO_CONNECTION_STRING"]
   # db_name = os.environ["MONGO_DBNAME"]
   # 
   # client = pymongo.MongoClient(connection_string)
   # db = client[db_name]
   # collection = db['Books']
   return render_template('home.html')


if __name__=="__main__":
    app.run(debug=True)