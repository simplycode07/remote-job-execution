from flask import Blueprint, flash, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user, login_user, logout_user, LoginManager

from werkzeug.security import check_password_hash, generate_password_hash

from .models import User, Job
from .executor_instantiated import executor
from . import db

view_routes = Blueprint("views", __name__)
login_manager = LoginManager()
login_manager.login_view = 'views.login'


def initialize_login(app):
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@view_routes.route("/submit", methods=["POST"])
def submit_job():
    command = request.form['command']
    job = Job(command=command, status='submitted', user_id=1)
    db.session.add(job)
    db.session.commit()

    executor.submit(job.id, command)
    return redirect('/jobs')

@view_routes.route("/")
@login_required
def jobs():
    user_id = current_user.id
    jobs = Job.query.filter_by(user_id=user_id).order_by(Job.created_at.desc()).all()
    return render_template('jobs.html', jobs=jobs)


@view_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        print(f"email = {email}, passwd = {password}")

        user = User.query.filter_by(email=email).first()
        if user and password:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash("logged in")
                return redirect(url_for("views.index"), code=302)

            else:
                flash("incorrect password")
        else:
            flash("you need to signup first")

    return render_template("login.html")


@view_routes.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.login"))


@view_routes.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        mobile = request.form.get("mobile")
        country_code = request.form.get("country_code")
        user_type_raw = request.form.get("user_type")
        user_type = UserType(0)

        try:
            user_type = UserType(user_type_raw)
        except ValueError:
            print("couldnt convert user to UserType")

        user = User.query.filter_by(email=email).first()

        if user:
            flash("email already in use")
            return redirect(url_for("views.login"))

        elif password:
            if len(User.query.all()) == 0:
                new_user = User(first_name=first_name,
                                last_name=last_name,
                                email=email,
                                password=generate_password_hash(password),
                                mobile=mobile,
                                country_code=country_code,
                                user_type=user_type
                                )

                db.session.add(new_user)
                db.session.commit()

            return redirect(url_for("views.login"))

        else:
            flash("Password Empty")

    return render_template("signup.html")
