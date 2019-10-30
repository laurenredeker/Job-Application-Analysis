# Imports
import pandas as pd
import numpy as np
import seaborn as sns
import email, email.header, getpass, imaplib, os, re    #added email.header
from datetime import datetime
sns.set_style('whitegrid')

# Login to gmail
detach_dir = '.'
user = input("Enter your GMail username:")   ##change to raw_input if using 2
pwd = getpass.getpass("Enter your password: ")

# Connect to gmail imap sever
m = imaplib.IMAP4_SSL("imap.gmail.com")
m.login(user, pwd)

# Go to correct directory
m.select('"My Job App Folder"')   # you can specify which folder to look through

# Get the email ids
resp, items = m.search(None, "All")    #all mail
#resp, items = m.search(None, "All", r'X-GM-RAW "subject:\"Re\""')
### this was an attempt to categorize which emails were replies; found it easier to just include the sender addresses and then filter out my email address ###

items = items[0].split()

# Initialize lists
text = []
dates = []
subjects = []
sender = []


# Collect data
for emailid in items:
    
    # Fetch everything from the id
    resp, data = m.fetch(emailid, "(RFC822)")
    
    # Get the content
    email_body = data[0][1]   #raw text of the whole email
    
    # Convert to mail object
    mail = email.message_from_bytes(email_body)
    
    # Get subject
    subjects.append(email.header.decode_header(mail['Subject'])[0][0])

    # Get sender
    ### did not include the sender column in my CSV ###
    sender.append(email.utils.parseaddr(mail['From']))
    
    # Get date
    date_tuple = email.utils.parsedate_tz(mail['Date'])
    dates.append(datetime.fromtimestamp(email.utils.mktime_tz(date_tuple)))
    
    # Get text
    if mail.is_multipart():        #if multipart is true, it is a list of message objects
        text.append(mail.get_payload(0).get_payload())
    else:			    #if multipart is false, it is a string
        text.append(mail.get_payload())


# Convert to dataframe
df = pd.DataFrame(data={'Date': dates, 'Subject': subjects, 'Sender': sender, 'Text': text})
df.head()

# Break up date column
df['Time'] = df['Date'].apply(lambda x: x.time())
df['Day'] = df['Date'].apply(lambda x: x.weekday()).map({0:'Mon', 1:'Tues', 2:'Weds', 
                                                         3:'Thurs', 4:'Fri', 5:'Sat', 6:'Sun'})
df['Hour'] = df['Time'].apply(lambda x: x.hour)
df = df[['Date', 'Time', 'Day', 'Hour', 'Sender', 'Subject', 'Text']]

# Preview data
#df.head()

# Data overview
#df.info()

# Export to csv
df.to_csv('sample.csv', index=False)

 



