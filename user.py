from flask import jsonify, render_template
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash

import random
from string import ascii_letters, digits
from passwordmeter import test

# from run import send_mail

import dbconnect

from validate_email import validate_email
from usernames import is_safe_username

MX_VERIFY = False
FULL_VERIFY = False


###########################################################################################################
def random_password(length=8):
    prg = random.SystemRandom()

    while 1:
        password = "".join(prg.choice(ascii_letters + digits) for _ in xrange(length))
        if is_strong_password(password):
            break
    return password


def is_strong_password(password):
    strength, improvements = test(password)
    if strength < 0.3:
        return False
    return True


###########################################################################################################
def register(value):
    email = value["email"]
    username = value["username"]
    password = value["password"]
    age = int(value["age"])
    gender = value["gender"]
    if validate_email(email, check_mx=MX_VERIFY, verify=FULL_VERIFY) == False:  # Only checking domain has SMTP Server
        return jsonify({"Status": 0, "Message": "Please enter a valid email address."})
    if not is_safe_username(username):
        return jsonify({"Status": 0, "Message": "Please enter a valid username."})
    if not is_strong_password(password):
        return jsonify({"Status": 0, "Message": "Your password is to weak, please try again."})

    con, c = dbconnect.connect()
    query = " SELECT user_id FROM user WHERE user_email = %s "
    if c.execute(query, (email,)) != 0:
        dbconnect.close(con, c)
        return jsonify({"Status": 0, "Message": "Email address has already been taken."})
    query = " SELECT user_id FROM user WHERE user_name = %s "
    if c.execute(query, (username,)) != 0:
        dbconnect.close(con, c)
        return jsonify({"Status": 0, "Message": "Username has already been taken."})

    pass_hash = generate_password_hash(password)

    query = " INSERT INTO user(user_email,user_name,pass_hash,age,gender) VALUES (%s,%s,%s,%s,%s);"

    c.execute(query, (email, username, pass_hash, age, gender))
    con.commit()
    dbconnect.close(con, c)

    html_msg = render_template("welcome.html", username=username)

    from run import send_mail
    send_mail("Welcome to Walk With Me", [email], html_msg)

    return jsonify({"Status": 1, "Message": "Registration successful! Please login."})


def login(value):
    login_name = value["login"]
    password = value["password"]
    con, c = dbconnect.connect()
    if validate_email(login_name):
        query = " SELECT * FROM user WHERE user_email = %s "
    else:
        query = " SELECT * FROM user WHERE user_name = %s "

    c.execute(query, (login_name,))
    row = c.fetchall()
    dbconnect.close(con, c)

    if len(row) != 0:
        row = row[0]
        pass_hash = row[3]
        if check_password_hash(pass_hash, password):
            valid_user = User(row[0], row[1], row[2], row[4], row[5])
            return (valid_user, jsonify({"Status": 1, "Message": "Logged in successfully."}))

    return (None, jsonify({"Status": 0, "Message": "Invalid username or password."}))


def change_password(uid, new_password):
    if not is_strong_password(new_password):
        return jsonify({"Status": 0, "Message": "Your password is to weak, please try again."})

    new_pass_hash = generate_password_hash(new_password)
    con, c = dbconnect.connect()
    query = " UPDATE user SET user.pass_hash = %s WHERE user.user_id = %s "
    c.execute(query, (new_pass_hash, uid))
    con.commit()
    dbconnect.close(con, c)

    return jsonify({"Status": 1, "Message": "Password changed successfully, please login again."})


def reset_password(login_name):
    con, c = dbconnect.connect()
    if validate_email(login_name):
        query = " SELECT * FROM user WHERE user_email = %s "
    else:
        query = " SELECT * FROM user WHERE user_name = %s "
    con, c = dbconnect.connect()
    c.execute(query, (login_name,))
    row = c.fetchall()
    if len(row) == 0:
        dbconnect.close(con, c)
    else:
        row = row[0]
        new_password = random_password()
        new_pass_hash = generate_password_hash(new_password)

        uid = row[0]
        email = row[1]
        username = row[2]
        query = " UPDATE user SET user.pass_hash = %s WHERE user.user_id = %s "
        c.execute(query, (new_pass_hash, uid))
        con.commit()
        dbconnect.close(con, c)

        html_msg = render_template("resetpassword.html", username=username, new_password=new_password)
        from run import send_mail
        send_mail("Walk With Me New Password", [email], html_msg)

    return jsonify({"Status": 1, "Message": "New password has been sent to your email address if the account exist."})


def update_profile(uid, email, age, gender, value):
    new_age = int(value["age"])
    new_gender = value["gender"]

    if (new_age != age) or (new_gender != gender):
        con, c = dbconnect.connect()
        query = "UPDATE user SET user.age = %s ,user.gender =%s WHERE user.user_id = %s "
        c.execute(query, (new_age, new_gender, uid))
        con.commit()
        dbconnect.close(con, c)
    return jsonify({"Status": 1, "Message": "Information changed successfully."})


###########################################################################################################
class User(UserMixin):
    def __init__(self, user_id, user_email, user_name, age, gender):
        self.user_id = int(user_id)
        self.user_email = user_email
        self.user_name = user_name
        self.age = int(age)
        self.gender = gender

    def get_age(self):
        return self.age

    def get_gender(self):
        return self.gender

    def get_email(self):
        return self.user_email

    def get_username(self):
        return self.user_name

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.user_id)

    def __repr__(self):
        return "<User %d>" % self.user_id
