from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, SearchForm
import os, logging, random
from sqlalchemy import inspect, func, MetaData, Table
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marchmessages44.sqlite'
app.config['SQLALCHEMY_BINDS'] = {'userdb': 'sqlite:///userdb.sqlite3'}
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_ECHO'] = True 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#################################################################

class User(UserMixin, db.Model):
    __bind_key__ = 'userdb'
    __tablename__ = 'user'
    
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

##########

class Message(db.Model):
    __tablename__ = 'messages'
    
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message_id = db.Column(db.Text)
    from_email = db.Column(db.Text)
    date       = db.Column(db.Text)
    to_email   = db.Column(db.Text)
    subject    = db.Column(db.Text)
    content    = db.Column(db.Text)


#################################################################

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_user_db():
    print(">> init_user_db")
    """Initialize the user database with a default admin user."""
    with app.app_context():
        # Get the userdb engine
        engine = db.engines['userdb']
        # Use the inspection API to check for the 'user' table
        inspector = inspect(engine)
        if not inspector.has_table(User.__tablename__):
            # Create the user table
            User.metadata.create_all(engine)
            # Add admin user
            admin_user = User(username='admin', password_hash=generate_password_hash('admin'))
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created with username 'admin' and password 'admin'")



####################################################################################

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('search'))
    return render_template('login.html', form=form)

####################################################################################
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    messages = []
    if request.method == 'POST' and form.validate_on_submit():
        search_query = form.search.data
        search_field = form.field.data
        match_type = form.match_type.data
        
        # Determine the type of match and construct the filter
        if match_type == 'partial':
            search_filter = getattr(Message, search_field).like(f'%{search_query}%')
        else:
            search_filter = getattr(Message, search_field) == search_query

        # Apply the filter to the query
        messages = Message.query.filter(search_filter).all()
    else:
        # If it's a GET request, show the first 10 messages
        print("Get request.")
        messages = Message.query.order_by(Message.id).limit(10).all()

    return render_template('search.html', form=form, messages=messages)

####################################################################################

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

####################################################################################
####################################################################################

# Reflect the existing database and map the Message model within the application context

Base = automap_base()

# Reflect the existing database and map the Message model within the application context
with app.app_context():
    # Reflect the schema from the database and map to the Base classes
    Base.prepare(db.engine, reflect=True)

    # Attempt to find the 'messages' class after reflection
    if 'messages' in Base.classes:
        Message = Base.classes.messages
        logger.info("The 'messages' table was found and mapped.")

        # Example usage of the Message mapped class
        # This should now work if the messages table exists in the database
        row_count = db.session.query(func.count(Message.id)).scalar()
        logger.info(f"Number of rows in 'messages' table: {row_count}")

        if row_count > 0:
            random_index = random.randint(0, row_count - 1)
            random_message = db.session.query(Message).offset(random_index).limit(1).first()
            if random_message:
                logger.info(f"Random 'from_email' from the 'messages' table: {random_message.from_email}")
            else:
                logger.info("Could not retrieve a random message.")
        else:
            logger.info("The 'messages' table is empty.")
    else:
        logger.error("The 'messages' table does not exist or could not be mapped.")


if __name__ == '__main__':
    with app.app_context():
        logger.info(f">>>> in app_context startup....")
        logger.info(f"> about to init the userdb if it does not exist")
        init_user_db()  # Initialize the user database with admin user

    app.run(debug=True, host = '0.0.0.0')

