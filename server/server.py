import re
import secrets
import sys

from flask import Flask, jsonify, render_template, request, url_for
from flask_mail import Mail, Message
from flask_mongoengine import MongoEngine
from flask_security import MongoEngineUserDatastore, Security, login_required
from passlib.apps import custom_app_context as pwd_context

import bcrypt
from flask_cors import CORS
from models import *

#=====================================================
# Constants
#=====================================================

json_tag = {'Content-Type': 'application/json'}

#=====================================================
# App skeleton
#=====================================================
# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = secrets.SECRET_KEY

# MongoDB Config
app.config['MONGODB_DB'] = 'mydatabase'
app.config['MONGODB_HOST'] = 'localhost'
app.config['MONGODB_PORT'] = 27017

# CORS Config
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Email Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = secrets.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = secrets.MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Create database connection object
db = MongoEngine(app)

# Define valid email, password patterns
email_pattern = re.compile('[\\w.]+@[\\w]+.[\\w]+', re.IGNORECASE)
max_email_length = 255
max_password_length = 255

# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)

#=====================================================
# Routes
#=====================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/protected')
@login_required
def protected():
    return 'This is a protected route.'

def send_email(text, recipients, subject="AR-top"):
    try:
        msg = Message(subject, sender="kruk@gmail.com", recipients=recipients)
        msg.body = text
        mail.send(msg)
    except Exception as e:
        app.logger.error("Failed to send message to " +
                         str(recipients) + "\n" + str(e))

@app.route('/api/register', methods=['POST'])
def register():
    # Confirm the request
    email, password = None, None
    try:
        # Use a dict access here, not ".get". The access is better with the try block.
        email = request.form["email"]
        password = request.form["password"]
    except:
        return jsonify(error="Malformed request; expecting email and password"), 422, json_tag

    # Validate the request
    if len(email) > max_email_length:
        return jsonify(error="Email can't be over " + str(max_email_length) + " characters."), 422, json_tag
    if not email_pattern.match(email):
        return jsonify(error="Email not valid."), 422, json_tag
    if len(password) < 8 or len(password) > max_password_length:
        return jsonify(error="Password must be between 8-" + str(max_password_length) + " characters."), 422, json_tag
    if not str.isalnum(password):
        return jsonify(error="Only alphanumeric characters are allowed in a password."), 422, json_tag

    # Try to retrieve a user object if it exists;
    user = User.objects(email=email)
    if len(user) != 0:
        return jsonify(error="Email already in use, please use another one"), 422, json_tag

    # Hash and create user
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    user_datastore.create_user(email=email, password=hashed)

    # So we can log user in automatically after registration
    token = User.objects(email=email)[0].generate_auth_token()

    # TODO: error handle this and if it doesn't work do something else besides the success in jsonify
    #send_email(recipients=[email], subject="ay whaddup", text="Hello from AR-top")

    return jsonify(success="Account has been created! Check your email to validate your account.", auth_token=token.decode('utf-8')), 200, json_tag

@app.route('/api/auth', methods=['POST'])
def authenticate():
    email, password = None, None
    try:
        # Use a dict access here, not ".get". The access is better with the try block.
        email = request.form["email"]
        password = request.form["password"]
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({"error": "Malformed Request; expecting email and password"}), 422, json_tag
  
    error = None
    user = User.objects(email=email)
    if len(user) == 0:
        error = "Incorrect email or password"
    elif len(user) > 1:
        error = "Incorrect email or password"
        app.logger.error("Someone registered the same email twice!")
    else:
        if bcrypt.checkpw(password.encode(), user[0].password.encode()):
            auth_token = user[0].generate_auth_token()
            # return username and auth token
            return jsonify({'email': user[0].email, 'auth_token': auth_token.decode('utf-8')}), 200, json_tag
        else:
            error = "Incorrect email or password"
    return jsonify({'error': error}), 422, json_tag

#=====================================================
# Main
#=====================================================
  
if __name__ == '__main__':
    from argparse import ArgumentParser
    
    parser = ArgumentParser(description="Runs flask server")
    
    # TODO: logic not implemented for this because we should wait
    parser.add_argument("mode", nargs='?', choices=[
                        'd', 'p'], help="Selects whether or not you want to run development or production")
    parser.add_argument("-e", "--email", nargs='+', type=str,
                        help="Sends an email if you use characters commandline can understand")
    parser.add_argument("-r", "--recipients", nargs='+',
                        type=str, help="Who you want to send to")
    parser.add_argument("-u", "--user", nargs=2, type=str,
                        help="Insert a new user: takes username, password")
    args = parser.parse_args()

    if args.email is not None:
        if args.recipients is None:
            print("You need to include recipients to email if you want to send an email.")
        else:
            send_email(text=' '.join(args.email), recipients=args.recipients)
        exit()

    app.run()
