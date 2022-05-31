from lib2to3.pgen2 import token
import os
from flask import Flask, render_template, request, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  desc, func
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta
from flask_mail import Mail, Message
from forms import RegistrationForm, LoginForm


app = Flask(__name__)
db = SQLAlchemy()
login_manager = LoginManager()


# nie odkryłem jeszcze czemu ale gdy konfiguracja apki jest na końcu w main to nic nie chce działać z funkcjonalności na macOS, aktualizowałem pythona itd i stypa XD

# # app.config['LOGIN_DISABLED'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'XDDDDD'
# db = SQLAlchemy(app)
# login_manager = LoginManager(app)
# login_manager.login_view = '/'




# ----------------------------------------------            const values for validation
NICKNAME_LENGTH_MIN = 5
NICKNAME_LENGTH_MAX = 50
PIN_LENGTH_MAX = 6
EMAIL_LENGTH_MAX = 100
SHOP_NAME_LENGTH_MAX = 50
PASSWORD_LENGTH_MIN = 8
PASSWORD_LENGTH_MAX = 32 #Odnoszę wrazenie ze trzeba to zmienić skoro będziemy uzywać hashowanych hasełek7
DELETE_COMMENT_AFTER=7

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
    product_id = db.Column(db.Integer)
    state=db.Column(db.Integer)
    date_of_deletion= db.Column(db.Date)
    how_many_likes = db.Column(db.Integer)

    def __init__(self, user_id,content,how_many_reports,product_id,state,date_of_deletion,how_many_likes):
        self.user_id=user_id
        self.content=content
        self.how_many_reports=how_many_reports
        self.product_id=product_id
        self.state=state
        self.date_of_deletion=date_of_deletion
        self.how_many_likes = how_many_likes

class authorization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    pin = db.Column(db.String(PIN_LENGTH_MAX))
    nickname = db.Column(db.String(NICKNAME_LENGTH_MAX))
    is_authenticated = db.Column(db.String(1))
    date_of_reset = db.Column(db.Date)

    def __init__(self, user_id,pin,nickname, is_authenticated, date_of_reset):
        self.user_id = user_id
        self.pin = pin
        self.nickname = nickname
        self.is_authenticated = is_authenticated
        self.date_of_reset = date_of_reset

class shop_preferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    shop_name = db.Column(db.String(SHOP_NAME_LENGTH_MAX))

    def __init__(self, user_id,shop_name):
        self.user_id = user_id
        self.shop_name = shop_name

#EXPERIMENTAL!
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    shop_name = db.Column(db.String(SHOP_NAME_LENGTH_MAX))
    price = db.Column(db.Integer)####shoud be REAL!!!!
    mark  = db.Column(db.String(100))

    def __init__(self, name, shop_name,price,mark):
        self.name = name
        self.shop_name = shop_name
        self.price= price
        self.mark= mark

class Reports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    comment_id = db.Column(db.Integer)

    def __init__(self, user_id, comment_id):
        self.user_id = user_id
        self.comment_id = comment_id


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    comment_id = db.Column(db.Integer)

    def __init__(self, user_id, comment_id):
        self.user_id = user_id
        self.comment_id = comment_id
# ---------------------------------------------                     admin_panel

def delete_old_comments():
    # czasowka na usuwanie komentarzy starych
    # komentarze maja stany 0 i 1
    # 0 - ok, 1 - do usuniecia
    # gdy stan == 0 to data jest 1900-01-01 w bazie
    # gdy stan == 1 to data jest dzisiaj +x czasu(zmienna globalna)
    # gdy roznica czasu bedzie <0 i data bedzie inna niz 1900-01-01 i stan ==1 to komentarz zostanie usuniety

    com = Comments.query.filter(Comments.state == 1)
    for i in com:
        tab = str(i.date_of_deletion - datetime.now().date())
        date_time_str = '1900-01-01'
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d')
        date_time_obj = datetime.date(date_time_obj)
        if (tab == '0:00:00'):
            x = 0
        else:
            tab = str(i.date_of_deletion - datetime.now().date()).split(" ")
            x = int(tab[0])
        if (x <= 0 and i.date_of_deletion != date_time_obj):
            reps=Reports.query.filter(Reports.comment_id==i.id)
            likes=Likes.query.filter(Likes.comment_id==i.id)
            for j in reps:
                db.session.delete(j)
            for j in likes:
                db.session.delete(j)
            db.session.delete(i)
            db.session.commit()

@app.route("/admin_show_x_users",methods = ['GET','POST'])
# @login_required
def admin_show_x_users():
    if (request.method == 'POST'):
        if(request.form.get('how_many')==""):
            flash("wprowadz liczbe!")
        else:
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
        if (request.form.get('how_many') == ""):
            flash("wprowadz liczbe!")
        else:
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
        if (request.form.get('how_many') == ""):
            flash("wprowadz liczbe!")
        else:
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
        mes_id=int(request.form.get('id'))
        com=Comments.query.filter(Comments.id==mes_id).first()
        if(com.state==1):
            com.state=0
            date_time_str = '1900-01-01'
            date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d')
            com.date_of_deletion=date_time_obj
        else:
            com.state=1
            com.date_of_deletion = datetime.now().date() + (timedelta(days=DELETE_COMMENT_AFTER))
        db.session.commit()
        return redirect("admin_index")

@app.route("/admin_comment_save",methods = ['GET','POST'])
# @login_required
def admin_comment_save():
    if (request.method == 'POST'):
        mes_id=request.form.get('id')
        com=Comments.query.filter(Comments.id==mes_id).first()
        com.how_many_reports=0
        reps = Reports.query.filter(Reports.comment_id == com.id)
        for j in reps:
            db.session.delete(j)
        db.session.commit()
        return redirect("admin_index")

@app.route("/admin_comment_save2",methods = ['GET','POST'])
# @login_required
def admin_comment_save2():
    if (request.method == 'POST'):
        mes_id=request.form.get('id')
        com=Comments.query.filter(Comments.id==mes_id).first()
        com.how_many_reports=0
        reps = Reports.query.filter(Reports.comment_id == com.id)
        for j in reps:
            db.session.delete(j)
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

def admin_comment_delete2():
    if (request.method == 'POST'):
        mes_id=request.form.get('id')
        com=Comments.query.filter(Comments.id==mes_id).first()

        # db.session.delete(com)
        # db.session.commit()
        if (com.state == 1):
            com.state = 0
        else:
            com.state = 1
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
@app.route("/")
@app.route("/home")
def main():
    return render_template('home.html')
@app.route('/user_panel')
#@login_required
def account():
    baza=[]
    user = User.query.filter(User.id == current_user.get_id).first()
    baza.append((user.nickname,user.age,user.sex,user.email))

    return render_template('user_panel.html',baza=baza)

@app.route('/delete_account', methods = ['GET','POST'])
#@login_required
def delete_account():
    flash("konto usuniete!", 'danger')
    return redirect("/")

@app.route('/opinions', methods = ['GET','POST'])
#@login_required
def opinions():
    return render_template('opinions.html')

@app.route('/fav_products', methods = ['GET','POST'])
#@login_required
def fav_products():
    records = []
    products = Product.query.all()
    records.append(products)
    return render_template('fav_products.html',records=records)

@app.route('/show_product', methods = ['GET','POST'])
#@login_required
def show_product():
    if (request.method == 'POST'):
        records = []
        combine = []
        display = ""
        id = int(request.form.get('id'))
        prod = Product.query.filter(Product.id == id)
        coms = Comments.query.filter(Comments.product_id == id)
        comments = []
        for i in coms:
            # l=Likes.query.filter(Likes.comment_id==i.id, Likes.user_id==current_user.id).first()
            l = Likes.query.filter(Likes.comment_id == i.id, Likes.user_id == 0).first()
            if (l != None):
                display = "liked"
            else:
                display = ""
            # r = Reports.query.filter(Reports.comment_id == i.id, Reports.user_id == current_user.id).first()
            r = Reports.query.filter(Reports.comment_id == i.id, Reports.user_id == 0).first()
            if (r != None):
                display2 = "red"
            else:
                display2 = ""

            comments.append(i)
            likess = i.how_many_likes
            combine.append((i, likess, display, id, display2))
        records.append(prod)
        records.append(combine)
        return render_template("product.html", records=records)


@app.route('/like_or_unlike_comment', methods = ['GET','POST'])
#@login_required
def like_or_unlike_comment():
    if (request.method == 'POST'):
        id=request.form.get('id')
        # l=Likes.query.filter(Likes.comment_id==id, Likes.user_id==current_user.id).first()
        l = Likes.query.filter(Likes.comment_id == id, Likes.user_id == 0).first()
        if(l!=None):
            db.session.delete(l)
        else:
            # l = Likes(current_user.id, id)
            l=Likes(0,id)
            db.session.add(l)
        db.session.commit()

        records = []
        combine = []
        display = ""
        display2 = ""
        id = int(request.form.get('product_id'))
        prod = Product.query.filter(Product.id == id)
        coms = Comments.query.filter(Comments.product_id == id)
        comments = []
        for i in coms:
            # l=Likes.query.filter(Likes.comment_id==i.id, Likes.user_id==current_user.id).first()
            l = Likes.query.filter(Likes.comment_id == i.id, Likes.user_id == 0).first()
            if (l != None):
                display = "liked"
            else:
                display = ""
            # r = Reports.query.filter(Reports.comment_id == i.id, Reports.user_id == current_user.id).first()
            r = Reports.query.filter(Reports.comment_id == i.id, Reports.user_id == 0).first()
            if (r != None):
                display2 = "red"
            else:
                display2 = ""

            comments.append(i)
            likess = Likes.query.filter(Likes.comment_id == i.id).count()
            i.how_many_likes = likess
            db.session.commit()
            combine.append((i, likess, display, id, display2))
        records.append(prod)
        records.append(combine)
        return render_template("product.html", records=records)

@app.route('/report_comment', methods = ['GET','POST'])
#@login_required
def report_comment():
    if (request.method == 'POST'):
        id=request.form.get('id')
        # l=Reports.query.filter(Reports.comment_id==id, Reports.user_id==current_user.id).first()
        l = Reports.query.filter(Reports.comment_id == id, Reports.user_id == 0).first()
        if(l!=None):
            db.session.delete(l)
        else:
            # l = Reports(current_user.id, id)
            l=Reports(0,id)
            db.session.add(l)
        db.session.commit()

        records = []
        combine = []
        display = ""
        display2=""
        id = int(request.form.get('product_id'))
        prod = Product.query.filter(Product.id == id)
        coms = Comments.query.filter(Comments.product_id == id)
        comments = []
        for i in coms:
            # l=Likes.query.filter(Likes.comment_id==i.id, Likes.user_id==current_user.id).first()
            l = Likes.query.filter(Likes.comment_id == i.id, Likes.user_id == 0).first()
            if (l != None):
                display = "liked"
            else:
                display = ""
            # r = Reports.query.filter(Reports.comment_id == i.id, Reports.user_id == current_user.id).first()
            r = Reports.query.filter(Reports.comment_id == i.id, Reports.user_id == 0).first()
            if (r != None):
                display2 = "red"
            else:
                display2 = ""

            comments.append(i)
            likess = Likes.query.filter(Likes.comment_id == i.id).count()
            repss = Reports.query.filter(Reports.comment_id == i.id).count()
            i.how_many_reports = repss
            db.session.commit()
            combine.append((i, likess, display, id, display2))
        records.append(prod)
        records.append(combine)
        return render_template("product.html", records=records)


@app.route('/edit_account', methods = ['GET','POST'])
#@login_required
def edit_account():
    return render_template('edit_account.html')


@app.route('/add_comment', methods = ['GET','POST'])
#@login_required
def add_comment():
    if (request.method == 'POST'):
        id=request.form.get('id')
        com=request.form.get('komentarz')
        date_time_str = '1900-01-01'
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d')
        #'AnonymousUserMixin' object has no attribute 'id'!!!!!!!!!!!!!!!!!!!!!!!!1 nie pojdzie bez logowania
        # c=Comments(current_user.id, com,0,id,0,date_time_obj)
        c = Comments(1, com, 0, id, 0, date_time_obj,0)
        db.session.add(c)
        db.session.commit()

        records = []
        combine = []
        display = ""
        id = int(request.form.get('id'))
        prod = Product.query.filter(Product.id == id)
        coms = Comments.query.filter(Comments.product_id == id)
        comments = []
        for i in coms:
            # l=Likes.query.filter(Likes.comment_id==i.id, Likes.user_id==current_user.id).first()
            l = Likes.query.filter(Likes.comment_id == i.id, Likes.user_id == 0).first()
            if (l != None):
                display = "liked"
            else:
                display = ""
            # r = Reports.query.filter(Reports.comment_id == i.id, Reports.user_id == current_user.id).first()
            r = Reports.query.filter(Reports.comment_id == i.id, Reports.user_id == 0).first()
            if (r != None):
                display2 = "red"
            else:
                display2 = ""

            comments.append(i)
            likess = Likes.query.filter(Likes.comment_id == i.id).count()
            combine.append((i, likess, display, id, display2))
        records.append(prod)
        records.append(combine)
        return render_template("product.html", records=records)

# ---------------------------------------------                     end_of_user_panel

# ---------------------------------------------                     register_panel
@app.route('/register', methods= ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RegistrationForm()
    userCheck = User.query.filter_by(nickname=form.username.data).first()
    userMail = User.query.filter_by(email=func.lower(form.email.data)).first() 
    
    if form.validate_on_submit():
        if userCheck:
            flash('Nickname jest juz zajęty!', 'danger') 
        elif userMail:
            flash('Email jest juz zajęty!', 'danger')
        else:
            passwordHashed = generate_password_hash(form.password.data)
            user = User(form.username.data, form.email.data, passwordHashed, form.age.data, form.sex.data, 0)
            db.session.add(user)
            db.session.commit()
            flash(f'Zarejestrowano pomyślnie!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Rejestracja', form=form)


# ---------------------------------------------                     end_of_register_panel

# ---------------------------------------------                     login_panel
@app.route("/login", methods= ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=func.lower(form.email.data)).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Zalogowano pomyślnie!", 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main'))
        else:
            flash('Logowanie nieudane, sprawdź poprawność adresu e-mail i hasła!', 'danger')
    return render_template('login.html', title='Logowanie', form=form)

# ---------------------------------------------                     end_of_login_panel
@app.route("/logout", methods= ['GET',])
def logout():
    logout_user()
 
    return redirect(url_for('main'))

@app.route("/")
def index():
    return "hello world!"


if __name__ == "__main__":
    # app.config['LOGIN_DISABLED'] = True
    db.create_all(app=app)
    app.run(host='0.0.0.0', debug=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SECRET_KEY'] = 'XDDDDD'
    db.init_app(app)
    login_manager.login_view = '/'
    login_manager.init_app(app)
    db.create_all(app=app)
    app.run(host='0.0.0.0', debug=True)
