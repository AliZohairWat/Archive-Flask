from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField
from passlib.hash import sha256_crypt
 
app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Alizohair1'
app.config['MYSQL_DB'] = 'flaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)

DummyArticles = Articles()

# Home Page
@app.route('/')
def run():
    return render_template('home.html')

# About Page
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
    fname = StringField('First Name', [validators.Length(min=3, max=20, message='The First Name should be between 3 and 20 letters long')])
    lname = StringField('Last Name', [validators.Length(min=1, max=20)])
    age = IntegerField('Age', [validators.NumberRange(min=18)])
    email = StringField('Email', [validators.Length(min=6, max=35)])
    username = StringField('Username', [validators.Length(min=1, max=10)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route('/register', methods=['GET', 'POST'])

def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        fname = form.fname.data
        lname = form.lname.data
        age = form.age.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        

        #MySQL Cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(fname, lname, username, email, password, age) VALUES(%s, %s, %s, %s, %s, %s)", (fname, lname, username, email, password, age))
        
        #Commit to MySQL
        mysql.connection.commit()

        #Close MySQL Connection
        cur.close()

        flash('You are now registered and can login to see the articles', 'success')


        redirect(url_for('register'))
    return render_template('register.html', form=form)

# User Login
@app.route('/login', methods=["GET", "POST"])

def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        #using db to verify password
        cur = mysql.connection.cursor()

        # Get relevant row based on username
        row = cur.execute('SELECT * FROM users WHERE username = %s', [username])

        if row > 0:
            # Get hash
            data = cur.fetchone()
            password = data['password']

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                #Pass
                session['logged_in'] = True
                session['username'] = username
                
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                #Wrong Password
                error = 'Your username or password is incorrect'
                return render_template('login.html', error=error)
            # Close db connection
            cur.close()
        else:
            # No such username
            error = 'Your username or password is incorrect'
            return render_template('login.html', error=error)
    return(render_template('login.html'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out. Please come again', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard', methods = ['GET', 'POST'])
# Dashboard

def dashboard():

    return render_template('dashboard.html')
if __name__ == '__main__':
    app.secret_key='secret'
    app.run(debug=True)
