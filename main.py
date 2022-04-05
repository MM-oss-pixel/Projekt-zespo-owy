from lib2to3.pgen2 import token
import os
from flask import Flask, render_template, request, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  desc
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

HOW_MANY_USERS_TO_SHOW=10
HOW_MANY_REPORTED_COMMENTS_TO_SHOW=10
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

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    content = db.Column(db.String(EMAIL_LENGTH_MAX))
    how_many_reports = db.Column(db.Integer)

    def __init__(self, user_id,content,how_many_reports):
        self.user_id=user_id
        self.content=content
        self.how_many_reports=how_many_reports

# ---------------------------------------------                     admin_panel

@app.route("/admin_show_x_users",methods = ['GET','POST'])
# @login_required
def admin_show_x_users():
    if (request.method == 'POST'):
        how_many=int(request.form.get('how_many'))
        global HOW_MANY_USERS_TO_SHOW
        HOW_MANY_USERS_TO_SHOW=how_many
        if(HOW_MANY_USERS_TO_SHOW<0):
            HOW_MANY_USERS_TO_SHOW=0
        return redirect("/admin_index")


@app.route("/admin_show_x_comments",methods = ['GET','POST'])
# @login_required
def admin_show_x_comments():
    if (request.method == 'POST'):
        how_many=int(request.form.get('how_many'))
        global HOW_MANY_REPORTED_COMMENTS_TO_SHOW
        HOW_MANY_REPORTED_COMMENTS_TO_SHOW=how_many
        if(HOW_MANY_REPORTED_COMMENTS_TO_SHOW<0):
            HOW_MANY_REPORTED_COMMENTS_TO_SHOW=0
        return redirect("/admin_index")

@app.route("/admin_show_x_comments2",methods = ['GET','POST'])
# @login_required
def admin_show_x_comments2():
    if (request.method == 'POST'):
        how_many=int(request.form.get('how_many'))
        global HOW_MANY_REPORTED_COMMENTS_TO_SHOW
        HOW_MANY_REPORTED_COMMENTS_TO_SHOW=how_many
        if(HOW_MANY_REPORTED_COMMENTS_TO_SHOW<0):
            HOW_MANY_REPORTED_COMMENTS_TO_SHOW=0
        userid=(request.form.get('id'))
        us = User.query.filter(User.id == userid).first()
        records = []
        x = []
        x.append(us)
        records.append(x)

        comments_of_user = Comments.query.filter(Comments.user_id == us.id).order_by(desc(Comments.how_many_reports)).limit(HOW_MANY_REPORTED_COMMENTS_TO_SHOW).all()
        x = []
        for i in comments_of_user:
            x.append(i)
        records.append(x)
        records.append(HOW_MANY_REPORTED_COMMENTS_TO_SHOW)
    return render_template("admin_check_user.html", records=records)

@app.route("/admin_index")
# @login_required
def admin_index():
    first_x_users=User.query.limit(HOW_MANY_USERS_TO_SHOW).all()
    x=[]
    for i in first_x_users:
        x.append(i)
    records=[]
    records.append(x)

    reported_comments=Comments.query.filter(Comments.how_many_reports>0).order_by(desc(Comments.how_many_reports)).limit(HOW_MANY_REPORTED_COMMENTS_TO_SHOW).all()
    x=[]
    for i in reported_comments:
        x.append(i)
    records.append(x)
    records.append(HOW_MANY_USERS_TO_SHOW)
    records.append(HOW_MANY_REPORTED_COMMENTS_TO_SHOW)
    return render_template("admin_index.html",records=records)


@app.route("/admin_search_user_by_nickname",methods = ['GET','POST'])
# @login_required
def admin_search_user_by_nickname():
    if (request.method == 'POST'):
        nickname=request.form.get('nickname')
        us=User.query.filter(User.nickname==nickname).first()
        if (len(nickname) == 0 or us==None):
            flash("podany user nie istnieje!")
            return redirect("/admin_index")
        records=[]
        x=[]
        x.append(us)
        records.append(x)

        comments_of_user=Comments.query.filter(Comments.user_id==us.id).order_by(desc(Comments.how_many_reports)).limit(HOW_MANY_REPORTED_COMMENTS_TO_SHOW).all()
        x=[]
        for i in comments_of_user:
            x.append(i)
        records.append(x)
        records.append(HOW_MANY_REPORTED_COMMENTS_TO_SHOW)
    return render_template("admin_check_user.html",records=records)


@app.route("/admin_search_user_by_id",methods = ['GET','POST'])
# @login_required
def admin_search_user_by_id():
    if (request.method == 'POST'):
        id=request.form.get('id')
        us=User.query.filter(User.id==id).first()
        if (len(id) == 0 or us==None):
            flash("podany user nie istnieje!")
            return redirect("/admin_index")
        records=[]
        x=[]
        x.append(us)
        records.append(x)

        comments_of_user=Comments.query.filter(Comments.user_id==us.id).order_by(desc(Comments.how_many_reports)).limit(HOW_MANY_REPORTED_COMMENTS_TO_SHOW).all()
        x=[]
        for i in comments_of_user:
            x.append(i)
        records.append(x)
        records.append(HOW_MANY_REPORTED_COMMENTS_TO_SHOW)
    return render_template("admin_check_user.html",records=records)


@app.route("/admin_search_user_by_email",methods = ['GET','POST'])
# @login_required
def admin_search_user_by_email():
    if (request.method == 'POST'):
        email=request.form.get('email')
        us=User.query.filter(User.email==email).first()
        if (len(email) == 0 or us==None):
            flash("podany user nie istnieje!")
            return redirect("/admin_index")
        records=[]
        x=[]
        x.append(us)
        records.append(x)

        comments_of_user=Comments.query.filter(Comments.user_id==us.id).order_by(desc(Comments.how_many_reports)).limit(HOW_MANY_REPORTED_COMMENTS_TO_SHOW).all()
        x=[]
        for i in comments_of_user:
            x.append(i)
        records.append(x)
        records.append(HOW_MANY_REPORTED_COMMENTS_TO_SHOW)
    return render_template("admin_check_user.html",records=records)


@app.route("/admin_comment_delete",methods = ['GET','POST'])
# @login_required
def admin_comment_delete():
    if (request.method == 'POST'):
        mes_id=request.form.get('id')
        com=Comments.query.filter(Comments.id==mes_id).first()

        db.session.delete(com)
        db.session.commit()
        return redirect("admin_index")

@app.route("/admin_comment_save",methods = ['GET','POST'])
# @login_required
def admin_comment_save():
    if (request.method == 'POST'):
        mes_id=request.form.get('id')
        com=Comments.query.filter(Comments.id==mes_id).first()
        com.how_many_reports=0
        db.session.commit()
        return redirect("admin_index")

@app.route("/admin_comment_save2",methods = ['GET','POST'])
# @login_required
def admin_comment_save2():
    if (request.method == 'POST'):
        mes_id=request.form.get('id')
        com=Comments.query.filter(Comments.id==mes_id).first()
        com.how_many_reports=0
        db.session.commit()

        userid = com.user_id
        us = User.query.filter(User.id == userid).first()
        records = []
        x = []
        x.append(us)
        records.append(x)

        comments_of_user = Comments.query.filter(Comments.user_id == us.id).order_by(
            desc(Comments.how_many_reports)).limit(HOW_MANY_REPORTED_COMMENTS_TO_SHOW).all()
        x = []
        for i in comments_of_user:
            x.append(i)
        records.append(x)
        records.append(HOW_MANY_REPORTED_COMMENTS_TO_SHOW)
    return render_template("admin_check_user.html", records=records)

@app.route("/admin_comment_delete2",methods = ['GET','POST'])
# @login_required
def admin_comment_delete2():
    if (request.method == 'POST'):
        mes_id=request.form.get('id')
        com=Comments.query.filter(Comments.id==mes_id).first()

        db.session.delete(com)
        db.session.commit()

        userid=com.user_id
        us = User.query.filter(User.id == userid).first()
        records = []
        x = []
        x.append(us)
        records.append(x)

        comments_of_user = Comments.query.filter(Comments.user_id == us.id).order_by(
            desc(Comments.how_many_reports)).limit(HOW_MANY_REPORTED_COMMENTS_TO_SHOW).all()
        x = []
        for i in comments_of_user:
            x.append(i)
        records.append(x)
        records.append(HOW_MANY_REPORTED_COMMENTS_TO_SHOW)
    return render_template("admin_check_user.html", records=records)

@app.route("/admin_user_edit_proceed",methods = ['GET','POST'])
# @login_required
def admin_user_edit_proceed():
    if (request.method == 'POST'):
        id=request.form.get('id')
        nickname=request.form.get('nickname')
        email = request.form.get('email')
        password=request.form.get("password")
        age = request.form.get('age')
        sex = request.form.get('sex')
        is_admin = request.form.get('is_admin')

        us=User.query.filter(User.id==id).first()
        us.id=id
        us.nickname=nickname
        us.email=email
        us.password=password
        us.age=age
        us.sex=sex
        us.is_admin=is_admin
        db.session.commit()
        return redirect("admin_index")

# ---------------------------------------------                     end_of_admin_panel

# ---------------------------------------------                     user_panel
# @app.route("/")
# @app.route("/home")
# def main():
#     return render_template('home.html')
# @app.route('/user_panel')
# #@login_required
# def account():
#     baza=[]
#     return render_template('user_panel.html',baza=baza)

# @app.route('/delete_account', methods = ['GET','POST'])
# #@login_required
# def delete_account():
#     flash("konto usuniete!", 'danger')
#     return redirect("/")

# @app.route('/opinions', methods = ['GET','POST'])
# #@login_required
# def opinions():
#     return render_template('opinions.html')

# @app.route('/fav_products', methods = ['GET','POST'])
# #@login_required
# def fav_products():
#     return render_template('fav_products.html')

# @app.route('/edit_account', methods = ['GET','POST'])
# #@login_required
# def edit_account():
#     return render_template('edit_account.html')

# ---------------------------------------------                     end_of_user_panel


@app.route("/")
def index():
    return "hello world!"


if __name__ == "__main__":
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SECRET_KEY'] = 'XDDDDD'
    db.init_app(app)
    login_manager.login_view = '/'
    login_manager.init_app(app)
    db.create_all(app=app)
    app.run(host='0.0.0.0', debug=True)
