from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField
from passlib.hash import sha256_crypt
from functools import wraps
 
app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Alizohair1'
app.config['MYSQL_DB'] = 'flaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)

# DummyArticles = Articles()

# Home Page
@app.route('/')
def run():
    return render_template('home.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Articles Page
@app.route('/articles')
def articles():
       # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute('SELECT * FROM articles')

    articles = cur.fetchall()
    
    if result > 0: 
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)
    

# Individual Article Page
@app.route('/article/<string:id>/')
def article(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles WHERE id=%s", [id])
    article = cur.fetchone()
    cur.close()
    return render_template('article.html', article=article)

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
    return (render_template('login.html'))

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized Access', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout Route
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out. Please come again', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard', methods = ['GET', 'POST'])
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute('SELECT * FROM articles')

    articles = cur.fetchall()
    
    if result > 0: 
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    
    return render_template('dashboard.html')

# Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=3, max=50, message='The Title should be between 3 and 20 letters long')])
    body = TextAreaField('Body', [validators.Length(min=30)])
 
# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Add Article to database
        # Locate Author Real Name
        # cur.execute("SELECT fname FROM users WHERE username=%s", (session['username']))
        # author_name = cur.fetchone()
        # print(author_name)

        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))
        mysql.connection.commit()
        cur.close()

        flash('Artice Successfully Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)
        
# Edit Article
@app.route('/edit_article/<string:id>', methods = ['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    cur.execute('SELECT * FROM articles WHERE id=%s', [id])
    article = cur.fetchone()

    # Get Form
    form = ArticleForm(request.form)
 
    # Fill article form fields
    form.title.data = article['title']
    form.body.data = article['body']


    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Add Article to database
        # Locate Author Real Name
        # cur.execute("SELECT fname FROM users WHERE username=%s", (session['username']))
        # author_name = cur.fetchone()
        # print(author_name)

        cur.execute("UPDATE articles SET title=%s, body=%s WHERE id=%s", (title, body, id))
        mysql.connection.commit()
        cur.close()

        flash('Artice Successfully Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)

@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Move articles to deleted_articles table
    cur.execute('INSERT INTO deleted_articles SELECT * FROM articles WHERE id=%s', (id))
    
    # Delete article
    cur.execute('DELETE FROM articles WHERE id=%s', (id))

    # Commit to db
    mysql.connection.commit()
    cur.close()

    flash('Article Successfully Deleted', 'success')

    return redirect(url_for('dashboard'))




if __name__ == '__main__':
    app.secret_key='secret'
    app.run(debug=True)
