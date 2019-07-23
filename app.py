from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField
from passlib.hash import sha256_crypt
 
app = Flask(__name__)

DummyArticles = Articles()

@app.route('/')
def run():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = DummyArticles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

class RegisterForm(Form):
    fname = StringField('First Name', [validators.Length(min=1, max=20)])
    lname = StringField('Last Name', [validators.Length(min=1, max=20)])
    age = IntegerField(' Age', [validators.NumberRange(min=18)])
    username = StringField('Username', [validators.Length(min=1, max=10)])
    email = StringField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST;'])

def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        return render_template('register.html', form=form)
    return render_template('register.html', form=form)
if __name__ == '__main__':
    app.run(debug=True)
