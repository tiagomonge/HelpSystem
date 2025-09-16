from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.forms import LoginForm, RegistrationForm, TicketForm
from flask import render_template, flash, redirect, url_for, abort
from app import db
from app.models import User
import sqlalchemy as sa

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('main'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/main')
@login_required
def main():
    return render_template('main.html', title='Home', user=current_user.name)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/tickets', methods=['GET', 'POST'])
@login_required
def tickets():
    form = TicketForm()
    if form.validate_on_submit():
        flash('Your ticket has been submitted!')
        return redirect(url_for('main'))
    return render_template('tickets.html', title='Tickets', form=form)


@app.route('/admin')
@login_required
def admin_panel():
    if current_user.type != "admin":
        abort(403)  # Forbidden
    return render_template("admin.html")