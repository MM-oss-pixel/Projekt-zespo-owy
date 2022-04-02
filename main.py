from lib2to3.pgen2 import token
import os
from flask import Flask, render_template, request, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_mail import Mail, Message

app = Flask(__name__)
db = SQLAlchemy()
login_manager = LoginManager()


# ----------------------------------------------            const values for validation
NICKNAME_LENGTH_MIN = 5
NICKNAME_LENGTH_MAX = 50

EMAIL_LENGTH_MAX = 100

PASSWORD_LENGTH_MIN = 8
PASSWORD_LENGTH_MAX = 32
# ----------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(NICKNAME_LENGTH_MAX))
    email = db.Column(db.String(EMAIL_LENGTH_MAX))
    password = db.Column(db.String(PASSWORD_LENGTH_MAX))
    age = db.Column(db.Integer)
    sex = db.Column(db.String(1))
    is_admin = db.Column(db.Integer)    #admin = 1, user = 0

    def __init__(self, nickname, email, password, age, sex, is_admin):
        self.nickname = nickname
        self.email = email
        self.password = password
        self.age=age
        self.sex= sex
        self.is_admin=is_admin



# ---------------------------------------------                     admin_panel

@app.route("/admin_index")
def admin_index():
    return render_template("admin_index.html")

# ---------------------------------------------                     end_of_admin_panel

@app.route("/")
def index():
    return "hello world!"


if __name__ == "__main__":
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SECRET_KEY'] = 'XDDDDD'
    db.init_app(app)
    login_manager.login_view = 'login'
    login_manager.init_app(app)
    db.create_all(app=app)
    app.run(host='0.0.0.0', debug=True)