#All python is made by SOUNDGOD aka CONSUN. This can be modifed and used for any project
import asyncio
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit
from passlib.hash import sha256_crypt
import pymysql
import os
import sys
import time
import operator
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta
from pymysql.err import OperationalError
from urllib.request import urlopen
import ssl
from flask_cors import CORS
import socketio 
import random
app = Flask(__name__)
@app.before_request
def make_session_permanent():
    session.permanent = True
messages = []
mariadb_connect = pymysql.connect(host="localhost",
                                  user="ploopitadmin",
                                  password="Pr0jectPl00p1t!!",
                                  database="Login",
                                  charset='utf8mb4',
                                  cursorclass=pymysql.cursors.DictCursor)

limiter = Limiter(app, default_limits=["200 per day", "50 per hour"])


class RestartServerEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(('.py', '.html', '.css', '.js')):
            print("Detected change in a file. Restarting server...")
            try:
                os.execv(sys.executable, [sys.executable] + sys.argv)
            except Exception as e:
                # Log the exception or handle it as needed
                print("Error while restarting the server:", e)

observer = Observer()
observer.schedule(RestartServerEventHandler(), path='.', recursive=True)
observer.start()

@app.route('/')
@limiter.limit("5 per minute")
def home():
  session['logged_in'] = ""
  return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def do_login():
    if request.method == "GET":
        return render_template('login.html')
    else:
        login = request.form
        userName = login['username']
        password = login['password']

        try:
            with mariadb_connect.cursor() as cursor:
                cursor.execute("SELECT * FROM Login WHERE username = %s", (userName,))
                data = cursor.fetchone()
                if data is None:
                    msg="account was not found"
                    return render_template('login.html', msg=msg)
                else:
                 if data and sha256_crypt.verify(password, data['password']):
                    if 'banned' in data:
                        session['banned'] = data['banned']
                        session['reason'] = data['reason']
                    session['logged_in'] = True
                    session['username'] = userName
                    if 'role' in data:
                        session['role'] = data['role']
                    if 'bubbles' in data:
                        session['bubbles'] = data['bubbles']
                        cursor.execute("SELECT * FROM Ploops WHERE username = %s", (userName,))
                        ploop = cursor.fetchone()
                        if 'unlocked' in data:
                         session['unlocked'] = ploop['unlocked']
                        if 'ploops' in data:
                         session['ploops'] = ploop['ploops']
                        if 'date' in data:
                         session['date'] = data['date']

                    else: 
                        session['bubbles'] = 0

                    print("Login successful. Redirecting to stats.")
                    return redirect("stats")
                 else:
                    print("Login failed. Redirecting to login.html.")
                    msg="incorrect username or password"
                    return render_template('login.html', msg=msg)

        except Exception as e:
            print("Error:", e)

    return render_template('login.html')


@app.route("/claiming", methods=['GET', 'POST'])
def claiming():
  if request.method == "GET":
    return redirect("stats")
  else:
    if session.get('dailybubbles') == True:
      last_claim_time = session.get('claim_time')

      if last_claim_time is not None:
        current_time = datetime.now()
        time_elapsed = current_time - last_claim_time
        if time_elapsed > timedelta(hours=24):
          session['dailybubbles'] = False
      else:
        session['dailybubbles'] = False
    else:
      try:
        userName = session['username']

        with mariadb_connect.cursor() as cursor:
          # Fetch the row with the user's information
          cursor.execute("SELECT * FROM Login WHERE username = %s",
                         (userName, ))
          user_row = cursor.fetchone()

          if user_row:
            current_bubbles = int(user_row['bubbles'])

            new_bubbles = current_bubbles + 1000

            cursor.execute("UPDATE Login SET bubbles = %s WHERE username = %s",
                           (new_bubbles, userName))
            mariadb_connect.commit()

            session['bubbles'] = new_bubbles
            session['dailybubbles'] = True
            session['claim_time'] = datetime.now()

      except Exception as e:
        print("Error:", e)

    return redirect("market")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        register = request.form
        userName = register['username']
        password = sha256_crypt.encrypt(register['password'])
        special_characters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '=', ';', ':', '"']
        character_limit = 16
        if len(userName) > character_limit:
            msg = "Username is too big"
            return render_template('register.html', msg=msg)
        else:
                for word in special_characters:
                    msg = "Username can't contain invalid characters"
                    return render_template('register.html', msg=msg)
        with mariadb_connect.cursor() as cursor:
                cursor.execute("SELECT * FROM Login WHERE username = %s", (userName,))
                data = cursor.fetchone()

                if data is not None:
                    message = "This username is taken"
                    return render_template('register.html', msg=message)
                else:
                    session['username'] = userName
                    bubbles = 0
                    banned = "false"
                    session['bubbles'] = bubbles
                    session['role'] = "New User"
                    cursor.execute(
                        'INSERT INTO Login (username, password, bubbles, banned) VALUES (%s, %s, %s, %s)',
                        (userName, password, bubbles, banned))
                    mariadb_connect.commit()
                    unlocked = 0
                    ploops = ""
                    cursor.execute(
                        'INSERT INTO Ploops (username, unlocked, ploops) VALUES (%s, %s, %s)',
                        (userName, unlocked, ploops))
                    mariadb_connect.commit()
                    session['unlocked'] = unlocked
                    session['ploops'] = ploops
                    session['banned'] = banned
                    message = "You are registered. Welcome to Xenostar."
                    session['logged_in'] = True
                    return redirect('stats')

    else:
        return render_template('register.html')



@app.route('/banuser', methods=['GET', 'POST'])
def banuser():
  if request.method == "GET":
    return redirect("admin")
  else:
    banform = request.form
    userName = banform['username']
    password = banform['adminpass']

    cur = mariadb_connect.cursor()

    if password == "9&9hg&$77":
      cur.execute("SELECT * FROM Login WHERE username = %s", (userName, ))
      cur.fetchone()
      cur.execute("UPDATE Login SET banned = 'true' WHERE username = %s",
                  (userName, ))

      reason = banform.get(
        'reason')

      if reason:
        cur.execute("UPDATE Login SET reason = %s WHERE username = %s",
                    (reason, userName))

      mariadb_connect.commit()
      cur.close()

    return redirect("admin")


@app.route('/unbanuser', methods=['GET', 'POST'])
def unbanuser():
  if request.method == "GET":
    return redirect("admin")
  else:
    banform = request.form
    userName = banform['username']
    password = banform['adminpass']

    cur = mariadb_connect.cursor()

    if password == "9&9hg&$77":
      cur.execute("SELECT * FROM Login WHERE username = %s", (userName, ))
      cur.fetchone()
      cur.execute("UPDATE Login SET banned = 'false' WHERE username = %s",
                  (userName, ))

      reason = banform.get(
        'reason')

      if reason:
        cur.execute("UPDATE Login SET reason = '' WHERE username = %s",
                    (userName, ))

      mariadb_connect.commit()
      cur.close()

    return redirect("admin")
  

@app.route('/resetpass', methods=['GET', 'POST'])
def changepass():
    if request.method == "GET":
        return render_template('settings.html', user=session['username'], role=session['role'])
    else:
        passform = request.form
        userName = passform['username']
        password = sha256_crypt.encrypt(passform['password'])
        oldpass = passform['oldpass']

        cur = mariadb_connect.cursor()
        cur.execute("SELECT * FROM Login WHERE username = %s", (userName,))
        data = cur.fetchone()
        if data and sha256_crypt.verify(oldpass, data['password']):
         cur.execute("UPDATE Login SET password = %s WHERE username = %s",
                    (password, userName))

        mariadb_connect.commit()
        cur.close()
        msg = "Password reset, please log back in."
        session['username'] = ""
        session['role'] = ""
        session['banned'] = ""
        session['reason'] = ""
        return render_template('Login.html', msg=msg)

@app.route('/resetuser', methods=['GET', 'POST'])
def changeuser():
    if request.method == "GET":
        return render_template('settings.html', user=session['username'], role=session['role'])
    else:
        passform = request.form
        userName = passform['username']
        newuser = passform['newuser']
        password = passform['password']

        cur = mariadb_connect.cursor()
        cur.execute("SELECT * FROM Login WHERE username = %s", (userName,))
        data = cur.fetchone()
        if data and sha256_crypt.verify(password, data['password']):
         cur.execute("UPDATE Login SET username = %s WHERE username = %s",
                    (newuser, userName))

        mariadb_connect.commit()
        cur.close()
        msg = "Username changed, please log back in with the new username."
        session['username'] = ""
        session['role'] = ""
        session['banned'] = ""
        session['reason'] = ""
        return render_template('Login.html', msg=msg)

@app.route('/stats')
def stats():
  
  if session['logged_in'] == True and session['banned'] == "false":
    return render_template('stats.html',
                           user=session['username'],
                           bubbles=session['bubbles'],
                           role=session['role'], )
  elif session['banned'] == "true":
    return redirect("banned")
  else:
    return render_template('login.html', )
  
@app.route('/guestlogin')
def guestlogin():
 username='guest#'
 number=random.randint(1,1000)
 print(username)
 print(number)
 newusername = username + str(number)
 print(newusername)
 session['username'] = newusername
 session['bubbles'] = 0
 session['banned'] = "false"
 session['role'] = "guest"
 return render_template('stats.html', user=session['username'], role=session['role'], banned=session['banned'], bubbles=session['bubbles'])


@app.route('/market')
def market():
    userName = session['username']
    try:
        with mariadb_connect.cursor() as cursor:
            cursor.execute("SELECT * FROM Login WHERE username = %s", (userName,))
            data = cursor.fetchone()

        if 'banned' in data:
            session['banned'] = data['banned']
            session['reason'] = data['reason']
            
        if session['banned'] == "false":
            return render_template('market.html',
                                   user=session['username'],
                                   bubbles=session['bubbles'],
                                   )
        elif session['banned'] == "true":
            return redirect("banned")
        else:
            return render_template('login.html', )
    
    except Exception as e:
        return f"An error occurred: {str(e)}"


@app.route('/settings')
def settings():
    userName = session['username']
    try:
        with mariadb_connect.cursor() as cursor:
            cursor.execute("SELECT * FROM Login WHERE username = %s", (userName,))
            data = cursor.fetchone()

        if 'banned' in data:
            session['banned'] = data['banned']
            session['reason'] = data['reason']
            
        if session['banned'] == "false":
            return render_template('settings.html',
                                   user=session['username'], )
        elif session['banned'] == "true":
            return redirect("banned")
        else:
            return render_template('login.html', )
    
    except Exception as e:
        return f"An error occurred: {str(e)}"


@app.route('/about')
def credits():
  return render_template('about.html')


@app.route('/admin')
def admin_panel():
  if session['role'] == "Admin":
    return render_template('down.html', user=session['username'])
  elif session['role'] == "Owner":
      return render_template('down.html', user=session['username'])
  else:
    return redirect("stats")


@app.route('/banned')
def banned():
  return render_template('down.html',
                         user=session['username'],
                         reason=session['reason'])


@app.route('/logout')
def logout():
  session['logged_in'] = False
  session['username'] = ""
  session['bubbles'] = ""
  return redirect("/")

@app.route('/send_message', methods=['POST'])
def send_message():
    user = session['username']
    message = request.form.get('message')

    if message:
            messages.append({'username': user, 'message': message})
            return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Empty message'})

@app.route('/get_messages')
def get_messages():
    return jsonify({'messages': messages})

@app.route('/chat')
def chat():
    userName = session['username']
    try:
        with mariadb_connect.cursor() as cursor:
            cursor.execute("SELECT * FROM Login WHERE username = %s", (userName,))
            data = cursor.fetchone()

        if 'banned' in data:
            session['banned'] = data['banned']
            session['reason'] = data['reason']
            
        if session['banned'] == "false":
            return render_template({'chat.html'}, user=session['username'])
        elif session['banned'] == "true":
            return redirect("banned")
        else:
            return render_template('login.html')
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.errorhandler(404)
def not_found(e):
   return render_template("404.html")

@app.errorhandler(500)
def not_found(e):
  return render_template("500.html")

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    try:
        app.run(
            ssl_context=('/etc/letsencrypt/live/ploopit.org/fullchain.pem', '/etc/letsencrypt/live/ploopit.org/privkey.pem'),
            debug=True,
            host='0.0.0.0',
            port=443
        )
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
    except ssl.SSLEOFError as e:
        print("SSLEOFError occurred:", e)
    except Exception as e:
        print("An error occurred:", e)
