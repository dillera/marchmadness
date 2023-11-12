
from flask import Flask, render_template, redirect, url_for, request, session, abort
from werkzeug.security import check_password_hash, generate_password_hash
from forms import LoginForm, SearchForm
import os
import logging
import sqlite3
from urllib.parse import urlparse, urljoin

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.config['SECRET_KEY'] = 'your-secret-key'
DATABASE = 'marchmessages44.sqlite'
# Hardcoded user credentials
hashed_password = generate_password_hash('admin')


#class LoginForm(FlaskForm):
#    username = StringField('Username')
##    password = PasswordField('Password')
 #   submit = SubmitField('Login')

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # This enables column access by name: row['column_name']
    return db


####################################################################################

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # Check if the username and password are correct
        if username == 'admin' and check_password_hash(hashed_password, password):
            session['logged_in'] = True
            return redirect(url_for('search'))
        else:
            error = 'Invalid username or password.'
            return render_template('login.html', form=form, error=error)
    return render_template('login.html', form=form)

# Helper function to check if user is logged in
def is_logged_in():
    return session.get('logged_in')

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

####################################################################################

@app.route('/search', methods=['GET', 'POST'])

def search():
    logger.info(f">> route - /search")

    if not is_logged_in():
        return redirect(url_for('login'))
    else:
        form = SearchForm()
        messages = []
        if request.method == 'POST' and form.validate_on_submit():
            search_query = form.search.data
            search_field = form.field.data
            match_type = form.match_type.data
            
            # Use sqlite3 to search the messages
            db = get_db()
            cursor = db.cursor()
            
            # Construct the SQL query based on match type
            if match_type == 'partial':
                query = f"SELECT * FROM messages WHERE {search_field} LIKE ?"
                cursor.execute(query, ('%' + search_query + '%',))
            else:
                query = f"SELECT * FROM messages WHERE {search_field} = ?"
                cursor.execute(query, (search_query,))
            
            messages = cursor.fetchall()
            db.close()
        else:
            # Display the first 10 messages by default
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY id LIMIT 10")
            messages = cursor.fetchall()
            db.close()

        return render_template('search.html', form=form, messages=messages)

####################################################################################

@app.route('/logout')

def logout():
    logout_user()
    return redirect(url_for('login'))


####################################################################################
####################################################################################

if __name__ == '__main__':
     app.run(debug=True, host = '0.0.0.0')
