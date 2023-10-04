from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
from passlib.hash import sha256_crypt
import pymysql
import os
import operator
import requests
# Python standard libraries
import json
import os
import sqlite3

# Third-party libraries
from flask import Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from db import init_db_command
from user import User

# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Flask app setup
app = Flask(__name__)
#app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

#static_folder="/www/ploopit/static/"

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()
"""
mariadb_connect = pymysql.connect(host="localhost", 
        user="ploopitadmin", 
        password="Pr0j3ctPl00p1t!!", 
        database="Login",
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
"""
@app.route('/')
def index():
  #return render_template('index.html')
  if current_user.is_authenticated:
      return (
          "<p>Hello, {}! You're logged in! Email: {}</p>"
          "<div><p>Google Profile Picture:</p>"
          '<img src="{}" alt="Google profile pic"></img></div>'
          '<a class="button" href="/logout">Logout</a>'.format(
              current_user.name, current_user.email, current_user.profile_pic
          )
      )
  else:
      return '<a class="button" href="/login">Google Login</a>'

@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
  # Get authorization code Google sent back to you
  code = request.args.get("code")
  # Find out what URL to hit to get tokens that allow you to ask for
  # things on behalf of a user
  google_provider_cfg = get_google_provider_cfg()
  token_endpoint = google_provider_cfg["token_endpoint"]
  # Prepare and send a request to get tokens! Yay tokens!
  token_url, headers, body = client.prepare_token_request(
    token_endpoint,
    authorization_response=request.url,
    redirect_url=request.base_url,
    code=code
  )
  token_response = requests.post(
    token_url,
    headers=headers,
    data=body,
    auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
  )
  # Now that you have tokens (yay) let's find and hit the URL
  # from Google that gives you the user's profile information,
  # including their Google profile image and email
  userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
  uri, headers, body = client.add_token(userinfo_endpoint)
  userinfo_response = requests.get(uri, headers=headers, data=body)

  # Parse the tokens!
  client.parse_request_body_response(json.dumps(token_response.json()))

  # You want to make sure their email is verified.
  # The user authenticated with Google, authorized your
  # app, and now you've verified their email through Google!
  if userinfo_response.json().get("email_verified"):
    unique_id = userinfo_response.json()["sub"]
    users_email = userinfo_response.json()["email"]
    picture = userinfo_response.json()["picture"]
    users_name = userinfo_response.json()["given_name"]
  else:
    return "User email not available or not verified by Google.", 400
  # Create a user in your db with the information provided
  # by Google
  user = User(
    id_=unique_id, name=users_name, email=users_email, profile_pic=picture
  )

  # Doesn't exist? Add it to the database.
  if not User.get(unique_id):
    User.create(unique_id, users_name, users_email, picture)

  # Begin user session by logging the user in
  login_user(user)

  # Send user back to homepage
  return redirect(url_for("index"))

@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for("index"))

""" 
@app.route('/login', methods=['GET', 'POST'])
def do_admin_login():
  if request.method == "GET":
    return render_template('login.html')
  else:
    login = request.form
     
    userName = login['username']
    password = login['password']

    cur = mariadb_connect.cursor()
    data = cur.execute("SELECT * FROM Login WHERE username= '"+userName+"'")
    data = cur.fetchone()

    if sha256_crypt.verify(password, data['password']):
      account = True

      role = 'Admin'

    if account:
      session['logged_in'] = True
    else:
      return render_template('/login')
    return stats(userName)
"""
"""
@app.route('/register',methods=['GET', 'POST'])
def register():
  if request.method == "POST":
    register = request.form
    #DO THE REGISTER FUNCTION
    userName = register['username']
    password = sha256_crypt.encrypt(register['password'])
    cur = mariadb_connect.cursor()
    data = cur.execute("SELECT * FROM Login WHERE username= '"+userName+"'")
    data = cur.fetchone()

    if data is not None:
      message = "You exist, bro!"
      return render_template('register.html')
    else:
      cur = mariadb_connect.cursor()
      role = 'new user'
      cur.execute('INSERT INTO Login (username, password) VALUES (%s, %s)', (userName, password))
      mariadb_connect.commit()
      cur.close()
      message = "You are registered. Welcome to Ploopit."
      return stats(userName)
  else:
    return render_template('register.html')
    
  
@app.route('/stats')
def stats(username):
 session['logged_in'] = True
 return render_template('stats.html', user=username)

@app.route('/market')
def market():
 session['logged_in'] = True
 return render_template('market.html')

@app.route('/credits')
def credits():
 session['logged_in'] = True
 return render_template('credits.html')


@app.route('/logout')
def logout():
  session['logged_in'] = False
  return index()

@app.route('/market?')
def addploop(Ploops):
 session['logged_in'] = True
Ploops = ["Blue Jewel"]
Ploops.insert(1, "Blue Jewel")
print(Ploops)

@app.route('/guestlogin')
def guestlogin():
 session['logged_in'] = True
 return render_template('stats.html', user=guestuser, role=guestrole)
guestuser = 'guest123'
guestrole = 'guest'

@app.route('/privacy')
def privacy():
  session['logged_in'] = True
  return render_template('privacy.html')

@app.route('/terms')
def terms():
  session['logged_in'] = True
  return render_template('terms.html')
# app name
@app.errorhandler(404)
  
# inbuilt function which takes error as parameter
def not_found(e):
  
# defining function
  return render_template("404.html")

@app.errorhandler(500)
def internal_error(e):

    return render_template("500.html")
"""

if __name__ == "__main__":
  app.secret_key = os.urandom(12)
  app.run(ssl_context=('/etc/letsencrypt/live/ploopit.org/fullchain.pem', '/etc/letsencrypt/live/ploopit.org/privkey.pem'), debug=True,host='0.0.0.0', port=443)