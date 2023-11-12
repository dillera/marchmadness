import os
import mailbox
from sqlalchemy import create_engine, Column, Integer, Text, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the Message class using SQLAlchemy's declarative base
Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Text)
    from_email = Column(Text)
    date = Column(Text)
    to_email = Column(Text)
    subject = Column(Text)
    content = Column(Text)

# Path to the directory containing .mbox files
mbox_directory = '../midatlanticretro-messages-mbox/'
# SQLite database path
sqlite_path = 'sqlite:///marchmessages.db'


# Create an engine that the Session will use for connection resources
engine = create_engine(sqlite_path)

# Bind the engine to the base class. This makes the engine accessible to all the subclasses.
Base.metadata.bind = engine

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
session = Session()

# Create all tables by issuing CREATE TABLE commands to the database.
Base.metadata.create_all(engine)



# Function to parse and insert messages
def insert_messages_from_mbox(mbox_file_path):
    mbox = mailbox.mbox(mbox_file_path)
    count = 0  # Counter for processed messages
    for msg in mbox:
        # Check if the message is multipart
        if msg.is_multipart():
            content = ''
            for part in msg.walk():
                if part.is_multipart():
                    continue
                if part.get_content_type() == 'text/plain':
                    part_payload = part.get_payload(decode=True)
                    if part_payload is not None:
                        content += part_payload.decode('utf-8', errors='ignore')
        else:
            payload = msg.get_payload(decode=True)
            content = payload.decode('utf-8', errors='ignore') if payload is not None else ''

        message_id = msg.get('Message-ID', 'No Message-ID')
        from_email = msg.get('From', 'No From')
        date = msg.get('Date', 'No Date')
        to_email = msg.get('To', 'No To')
        subject = msg.get('Subject', 'No Subject')
        
        message = Message(
            message_id=message_id,
            from_email=from_email,
            date=date,
            to_email=to_email,
            subject=subject,
            content=content
        )
        
        session.add(message)
        count += 1  # Increment the counter
        
        # Commit after every 1000 processed messages
        if count % 1000 == 0:
            try:
                session.commit()
                print(f"Committed {count} messages so far...")
            except Exception as e:
                print(f"An error occurred: {e}")
                session.rollback()
                
    # Commit any remaining messages that didn't hit the 1000 mark
    try:
        session.commit()
    except Exception as e:
        print(f"An error occurred on final commit: {e}")
        session.rollback()


# Search for .mbox files and insert their messages
for root, dirs, files in os.walk(mbox_directory):
    for file in files:
        if file.endswith('.mbox'):
            print(f"Starting processing for: {file}")
            mbox_file_path = os.path.join(root, file)
            insert_messages_from_mbox(mbox_file_path)

# Close the session
session.close()

