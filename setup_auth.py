import sqlite3
from getpass import getpass
from werkzeug.security import generate_password_hash

# Function to create the users table if it doesn't exist
def create_user_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

# Function to insert a new user into the users table
def insert_new_user(cursor, username, password_hash):
    try:
        cursor.execute('INSERT INTO user (username, password_hash) VALUES (?, ?)', (username, password_hash))
    except sqlite3.IntegrityError:
        print("Error: That username already exists.")
    else:
        print(f"User {username} created successfully.")

# Connect to the SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect('userdb.sqlite3')
cursor = conn.cursor()

# Create the users table
create_user_table(cursor)

# Input username and password from the command line
username = input("Enter a username: ")
password = getpass("Enter a password: ")  # Using getpass to hide password input

# Hash the password
password_hash = generate_password_hash(password)

# Insert new user into the database
insert_new_user(cursor, username, password_hash)

# Commit changes and close the connection
conn.commit()
cursor.close()
conn.close()
