import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import sys
calc_dir = '/home/zerts/MIPT/Machine-learning-Instagram-analysis/predict_system'
scrabber_dir = '/home/zerts/MIPT/Machine-learning-Instagram-analysis/scrabber/scrabber'
sys.path.append(calc_dir)
sys.path.append(scrabber_dir)
import json
import vgg_app
# import caffe_flickr_app
import scrabber
app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py
# app.run(host='0.0.0.0', port=81)
# app.run(threaded=False)

MY_USERNAME = 'ohrana228'
MY_PASSWORD = 'GoStartUp1337'

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


def collect_data(username):
    instascrabber = scrabber.InstagramScrabber(username=MY_USERNAME, password=MY_PASSWORD)
    instascrabber.collect_images_with_followers(username=username, dir_to_save='./')

def clear_memory(username):
    os.system('rm -r ./' + username)

@app.route('/hey')
def show_output():
    os.chdir(calc_dir)
    messages = json.loads(request.args['messages'])
    collect_data(messages['username'])
    print('collected\n')
    objects = vgg_app.predict_user(messages['username'])
    # styles = caffe_flickr_app.predict_user(messages['username'])
    styles={}
    # clear_memory(messages['username'])
    return render_template('show_output.html', objects=objects, styles=styles)


@app.route('/', methods=['GET', 'POST'])
def input():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        messages = json.dumps({'username': username, 'password': password})
        # flash('You send the best request ever')
        return redirect(url_for('show_output', messages=messages))
    return render_template('input.html', error=error)
