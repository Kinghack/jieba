#!flask/bin/python
from flask import Flask, jsonify, render_template, flash, redirect
'''
from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired

from forms import *

from flask import abort
from flask import make_response
from flask import request
from flask import url_for
from flask.ext.httpauth import HTTPBasicAuth
'''
#from models import *


app = Flask(__name__) #, static_url_path = "")
# app.config.from_object('config')

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/')
def index():
    return "Hello m'fing World"  #render_template("root.html")

'''
@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # login and validate the user...
            #login_user(user)
            #flash('Login requested for Username"' + form.username.data)
            #return redirect("/index")
            global users              
            if form.username.data not in users:
                users[unicode(form.username.data)] = unicode(form.password.data)
            elif form.username.data in users:
                if users[form.username.data] == form.password.data:
                    global user
                    user = form.username.data
                    global tasks
                    tasks[unicode(user)] = []# {'id': 4, 'title': 't', 'description': 'd', 'done': 'F'}, {'id': 'YEAH!!'}]
                    Tasks = tasks[unicode(user)]
                    return render_template("index.html", user = user, tasks = Tasks)
                else:
                    return render_template("login_again.html", form = form)
    return render_template("login.html", form = form)

    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
    '''


if __name__ == '__main__':
    app.run(debug = True)

