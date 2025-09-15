from app import app
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'David S'}
    return render_template('index.html', title='Home', user=user)

#alteração Tiago Santos
@app.route('/login')
def login ()
    user = {'username': 'David S'}
    return render_template('login.html', title='Login', user=user)
    
@app.route('/register')
def register ()

    return render_template('register.html', title='Registo', user=user)
    
#alteração Tiago Santos

