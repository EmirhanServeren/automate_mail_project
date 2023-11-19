import pandas as pd
import time         # use time to work with dates and times
import json         # use json to read the protected keys
import smtplib      # use smtplib to send emails
import os                   # for directory operations
from pathlib import Path    # use pathlib to get the absolute path to the script's directory
# mysql connection related libraries
import mysql.connector
from mysql.connector import Error

# json read file to invoke when reading keys stored in a json file
def read_keys_from_json(filepath):
    with open(filepath) as config_file:
        return json.load(config_file)
# get the absolute path to the script's directory
script_dir = Path.cwd()

# connect to mysql database
def connect_mysql():
    keys = read_keys_from_json(os.path.join(script_dir, 'mysql_keys.json'))
    connection = mysql.connector.connect(
            host = keys['host'],
            user = keys['user'],
            database = keys['database'],
            password = keys['password'])
    if connection.is_connected():
        return connection
    else:
        return False
def read_data_from_mysql():
    connection = connect_mysql()
    show_db_query = "select * from people"
    with connection.cursor() as cursor:
        cursor.execute(show_db_query)           # executing the select query
        data_from_mysql = cursor.fetchall()     # retrieving the data
    # creating the pandas dataframe
    column_names = [desc[0] for desc in cursor.description]
    return pd.DataFrame(data_from_mysql, columns=column_names)      # return the dataframe as an output

# get today's date and tomorrow's date in each execution
def today_date_get():
    return time.strftime("%d/%m")
def tomorrow_date_get():
    today_date = today_date_get()
    return (pd.to_datetime(today_date, format='%d/%m') + pd.DateOffset(days=1)).strftime('%d/%m')
def date_matching(dataframe, today_date):
    dataframe['Birthdates']=pd.to_datetime(dataframe['Birthdates'],format='%Y-%m-%d')
    condition = dataframe['Birthdates'].dt.strftime('%d/%m') == today_date
    filtered_df = dataframe[condition]
    return filtered_df
# flags generated with respect to date_matching function
def today_birthdays_checker(df):
    if date_matching(df, today_date_get()).empty:
        return False
    else:
        return True
def tomorrow_birthdays_checker(df):
    if date_matching(df, tomorrow_date_get()).empty:
        return False
    else:
        return True
# combined flag for both today and tomorrow
def birthdays_notifier_checker(df):
    if tomorrow_birthdays_checker(df) == False and today_birthdays_checker(df) == False:
        return False
    else:
        return True
# message generator functions for mails
def today_birthdays_msg(df):
    if today_birthdays_checker(df):
        print_df = date_matching(df, today_date_get())
        if len(print_df) > 1:
            message = "There are birthdays today!\n"
            message += "\n".join(print_df['Name'] + ' ' + print_df['Surname'])
        else:
            message = "There is a birthday today!\n"
            message += "\n".join(print_df['Name'] + ' ' + print_df['Surname'])
        return message
    else:
        return None
def tomorrow_birthdays_msg(df):
    if tomorrow_birthdays_checker(df):
        print_df = date_matching(df, tomorrow_date_get())
        if len(print_df) > 1:
            message = "There are birthdays tomorrow!\n"
            message += "\n".join(print_df['Name'] + ' ' + print_df['Surname'])
        else:
            message = "There is a birthday tomorrow!\n"
            message += "\n".join(print_df['Name'] + ' ' + print_df['Surname'])
        return message
    else:
        return None

# create a context for mail server
def mail_context_generator():
    if birthdays_notifier_checker(read_data_from_mysql())==True:
        subject = 'Birthday Notifier!'
        if today_birthdays_checker(read_data_from_mysql())==True and tomorrow_birthdays_checker(read_data_from_mysql())==False:
            body = today_birthdays_msg(read_data_from_mysql())
        elif today_birthdays_checker(read_data_from_mysql())==False and tomorrow_birthdays_checker(read_data_from_mysql())==True:
            body = tomorrow_birthdays_msg(read_data_from_mysql())
        else:
            body = today_birthdays_msg(read_data_from_mysql()) + '\n' + tomorrow_birthdays_msg(read_data_from_mysql())
        return f'Subject: {subject}\n\n{body}'
    else:
        pass
# smtp function to send mails
def automated_mailing(receiver_email, mail_context):
    smtp_keys = read_keys_from_json(os.path.join(script_dir, 'smtp_keys.json'))   # read json to get smtp keys
    with smtplib.SMTP(smtp_keys['smtp_server'], smtp_keys['smtp_port']) as smtp:
        smtp.starttls()
        smtp.login(smtp_keys['smtp_username'], smtp_keys['smtp_password'])
        smtp.sendmail(smtp_keys['smtp_username'],       # sender email pre-declared
                receiver_email, mail_context)           # pass recipient email, and mail context as input parameters

# AND SEND THE MAIL!
if birthdays_notifier_checker(read_data_from_mysql())==True:
    automated_mailing('emirhanserveren@gmail.com', mail_context_generator())
else:
    #print('No birthdays today or tomorrow!')   # to test on the terminal
    pass    # but do nothing if there is no birthday today or tomorrow
