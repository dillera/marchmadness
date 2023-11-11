from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from getpass import getpass
from werkzeug.security import generate_password_hash

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)

# The engine should match the `userdb` bind URI
engine = create_engine('sqlite:///userdb.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

# Ask for username and password
username = input("Enter a username: ")
password = getpass("Enter a password: ")

# Create a new user instance
new_user = User(username=username, password_hash=generate_password_hash(password))

# Add and commit the new user
session.add(new_user)
session.commit()
session.close()
