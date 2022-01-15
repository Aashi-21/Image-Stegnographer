from flask import Flask, render_template, request, redirect, url_for, session,current_app,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
from PIL import Image
import stepic
import shutil
from datetime import timedelta
# from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

app = Flask(__name__, static_url_path = "/UPLOAD_TEXT_FOLDER", static_folder = "UPLOAD_TEXT_FOLDER")

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your password'
app.config['MYSQL_DB'] = 'pythonlogin'
app.config['UPLOAD_TEXT_FOLDER'] = 'UPLOAD_TEXT_FOLDER'
app.config['TEXT_CACHE_FOLDER'] = 'TEXT_CACHE_FOLDER'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# Intialize MySQL
mysql = MySQL(app)

mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your mail id'
app.config['MAIL_PASSWORD'] = 'Your mailid password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route("/sent", methods=['GET', 'POST'])
def mail_sent():
    if request.method == 'POST':
        message = request.form['message']
       
        

        msg = Message('This is the intended encrypted messege', sender = "sender's mail id ", recipients = [message])
        msg.body = "Hello User, This is the encrypted image you can use. Thank you."
        with app.open_resource("UPLOAD_TEXT_FOLDER\encrypted_text_image.png") as fp:
            msg.attach("UPLOAD_TEXT_FOLDER\encrypted_text_image.png", "encrypted_image/png", fp.read())

        
        #msg.attach(file)

        mail.send(msg)
        return render_template("home.html")

@app.route("/mail")
def send_mail():
    return render_template('mail.html')




@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)




# http://localhost:5000/python/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))



# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/encode')
def encode():
    if os.path.exists(current_app.config['TEXT_CACHE_FOLDER']):
        shutil.rmtree(
            current_app.config['TEXT_CACHE_FOLDER'], ignore_errors=False)
    else:
        print("Not Found")
    

    if os.path.exists(os.path.join(current_app.config['UPLOAD_TEXT_FOLDER'], "encrypted_text_image.png")):
        # print("Found")
        os.remove(os.path.join(
            current_app.config['UPLOAD_TEXT_FOLDER'], "encrypted_text_image.png"))
    else:
        print("Not found")
    return render_template('encode.html')


@app.route("/encode-result", methods=['POST', 'GET'])
def text_encode_result():
    if request.method == 'POST':
        message = request.form['message']
        if 'file' not in request.files:
            flash('No image found')
        file = request.files['image']

        if file.filename == '':
            flash('No image selected')

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                current_app.config['UPLOAD_TEXT_FOLDER'], filename))
            text_encryption = True
            encrypt_text(os.path.join(
                current_app.config['UPLOAD_TEXT_FOLDER'], filename), message)
        else:
            text_encryption = False
        result = request.form

        return render_template("encode-text.html", result=result, file=file, text_encryption=text_encryption, message=message)


def encrypt_text(image_1, message):
    im = Image.open(image_1)

    im1 = stepic.encode(im, bytes(str(message), encoding='utf-8'))
    im1.save(os.path.join(
        current_app.config['UPLOAD_TEXT_FOLDER'], "encrypted_text_image.png"))

@app.route("/decode")
def decode():
    return render_template("decode.html")


@app.route("/decode-result", methods=['POST', 'GET'])
def text_decode_result():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No image found')
        file = request.files['image']
        if file.filename == '':
            flash('No image selected')
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                current_app.config['UPLOAD_TEXT_FOLDER'], filename))
            text_decryption = True
            message = decrypt_text(os.path.join(
                current_app.config['UPLOAD_TEXT_FOLDER'], filename))
        else:
            text_decryption = False
        result = request.form
        return render_template("decode-text.html", result=result, file=file, text_decryption=text_decryption, message=message)


def decrypt_text(image_1):
    im2 = Image.open(image_1)
    stegoImage = stepic.decode(im2)
    return stegoImage

app.run(debug=True)
