from flask import Flask, request, jsonify, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_socketio import SocketIO, disconnect, emit

import functools
from collections import OrderedDict

import dbconnect
import user
import spot
import plan

# User Cache
CACHE_SIZE = 100
user_cache = OrderedDict()

###########################################################################################################
app = Flask(__name__)
app.secret_key = "$Lwh,4EF}G<c5AvB]Dgqf^}GXc+jM]Uh"

app.config.update(
    DEBUG=False,
    # EMAIL SETTINGS
    MAIL_SERVER='127.0.0.1',
    MAIL_PORT=25
)
mail = Mail(app)

socketio = SocketIO(app)


###########################################################################################################
def add_to_cache(valid_user):
    if len(user_cache) + 1 > CACHE_SIZE:
        user_cache.popitem(last=False)
    user_cache[valid_user.get_id()] = valid_user


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)

    return wrapped


def send_mail(subject, recipients, html_msg):
    try:
        msg = Message(subject,
                      sender="walk-with-me@ec2-52-58-151-224.eu-central-1.compute.amazonaws.com",
                      recipients=recipients)
        msg.html = html_msg
        mail.send(msg)
    except Exception, e:
        app.logger.error('Error when sending email: %s', e)


login_manager = LoginManager()
# login_manager.session_protection="strong"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    if user_id in user_cache:
        return user_cache[user_id]
    try:
        con, c = dbconnect.connect()
        query = " SELECT * FROM user WHERE user_id = %s "
        c.execute(query, (int(user_id),))
        row = c.fetchall()
        dbconnect.close(con, c)
        row = row[0]
        valid_user = user.User(row[0], row[1], row[2], row[4], row[5])
        add_to_cache(valid_user)
        return valid_user
    except Exception, e:
        return None


###########################################################################################################

@app.errorhandler(401)
@app.errorhandler(403)
def Unauthorized_exception(e):
    app.logger.error('HTTP Exception: %s', e)
    return jsonify({"Status": 0, "Message": "Unauthorized, please try to login. Details: " + repr(e)})


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(408)
@app.errorhandler(500)
@app.errorhandler(502)
@app.errorhandler(504)
def http_exception(e):
    app.logger.error('HTTP Exception: %s', e)
    return jsonify({"Status": 0, "Message": "HTTP error. Details: " + repr(e)})


@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', e)
    return jsonify({"Status": 0, "Message": "Unknown error, please try again. Details: " + repr(e)})


###########################################################################################################
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    value = request.json
    return user.register(value)


@app.route("/login", methods=["POST"])
def login():
    value = request.json
    valid_user, message = user.login(value)
    if valid_user is not None:
        login_user(valid_user, True, True)
        add_to_cache(valid_user)
    return message


@app.route("/logout")
@login_required
def logout():
    uid = current_user.get_id()
    if uid in user_cache:
        del user_cache[uid]
    logout_user()
    return jsonify({"Status": 1, "Message": "Logged out successfully."})


@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    uid = current_user.get_id()
    new_password = request.json["password"]
    return user.change_password(uid, new_password)


@app.route("/is_authenticated")
def is_authenticated():
    return jsonify({"Status": 1, "Message": (current_user.get_id() is not None)})


@app.route("/get_profile")
@login_required
def get_profile():
    info = dict()
    info["Status"] = 1
    info["username"] = current_user.get_username()
    info["email"] = current_user.get_email()
    info["age"] = current_user.get_age()
    info["gender"] = current_user.get_gender()
    return jsonify(info)


@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    uid = current_user.get_id()
    value = request.json
    if uid in user_cache:
        del user_cache[uid]
    return user.update_profile(uid, current_user.get_email(), current_user.get_age(), current_user.get_gender(), value)


@app.route("/reset_password/<login_name>")
def reset_password(login_name):
    return user.reset_password(login_name)


###########################################################################################################
@app.route("/save_spot", methods=["POST"])
@login_required
def save_spot():
    uid = current_user.get_id()
    value = request.json
    return spot.save_spot(uid, value)


@app.route("/get_spot")
@login_required
def get_spot():
    pass


###########################################################################################################
@app.route("/save_plan", methods=["POST"])
@login_required
def save_plan():
    uid = current_user.get_id()
    value = request.json
    return plan.save_plan(uid, value)


@app.route("/get_plan")
@login_required
def get_plan():
    uid = current_user.get_id()
    return plan.get_plan(uid)


###########################################################################################################
@socketio.on("connect")
# @authenticated_only
def on_connect():
    emit("connect")


@socketio.on("disconnect")
def on_disconnect():
    emit("disconnect")


@socketio.on("json")
# @authenticated_only
def on_json(value):
    emit("json", value, broadcast=True)


###########################################################################################################


# if __name__ == '__main__':
    # context = ('certificate.crt', 'privateKey.key')
    # socketio.run(app, host='127.0.0.1', port=5000, debug=True, ssl_context=context)
    # socketio.run(app,host='0.0.0.0',port=5000,debug = False,ssl_context=context)

# eventlet set up
if __name__ == '__main__':
    import os
    key = os.path.join(os.path.dirname(__file__), 'cert/key.pem')
    cert = os.path.join(os.path.dirname(__file__), 'cert/cert.pem')
    socketio.run(app, host='0.0.0.0', port=443, debug=False, keyfile=key, certfile=cert)
