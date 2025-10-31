
# Libraries needed:

# Requests
import requests 

# Pandas
import pandas as pd

# datetime
from datetime import datetime

#postgre connector
import psycopg2

#sqlalchemy to load data from pandas, SQLAlchemy for connecting Pandas and databases
from sqlalchemy import create_engine, text

#sending mail, libraries
import smtplib #sending
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
import email.encoders

import schedule
import time
import io


def send_mail(subject, body, filename, today):
    """
    Sends an email with a CSV attachment stored in memory (not from disk).
    'filename' here is the CSV text content not a file path.
    This is to ensure you dont keep recreating a new csv file eah time your script is run.
    
    Ciao!, Tbrown!
    """

    #Email details
    smtp_server = "smtp.gmail.com" # <-- default for gmail (change if you use a different mail client)
    smtp_port = 587 # <-- #default for gmail (change if you use a different mail client)
    sender_mail = "" # <-- insert your sender mail account as a string i.e "xyz@gmail.com"
    email_password = "" # <-- insert your gmail smtp password as a string, not your gmail password! (check online for how to get smtp detail for gmail.)
    receiver_mails = [] # <-- pass receiver emails and save to list of strings ["abc@gmail.com", "def@yahoo.com"...]
    
    
    # compose the mail (Default, leave as it is!)
    message = MIMEMultipart()
    message['From'] = sender_mail
    message['To'] = ", ".join(receiver_mails)
    message ['Subject'] = subject
    
    # attaching body
    message.attach(MIMEText(body, 'html')) # <-- change 'html' to 'plain' if you dont want to render html but plain text instead, html here is to be referenced later in the script!
    
    
    # This block attaches the CSV file (from memory, not file saved locally) 
    # csv creates only saves in memory instead not as a file, leave this block as default
    csv_part = MIMEApplication(filename, Name=f"crypto_data_{today}.csv") # <-- you can change csv_name if you wish
    csv_part['Content-Disposition'] = f'attachment; filename="crypto_data_{today}.csv"' #<-- you can change csv_name if you wish
    message.attach(csv_part)


    """ 
    if you will rather saved each file to pc locally each time you run script use this block below instead, 
    rather than that above.

    """
    # with open(filename, 'rb') as file:
    #     part = MIMEBase('application', 'octet-stream')
    #     part.set_payload(file.read())
    #     email.encoders.encode_base64(part)  # This line encodes the file in base64 (optional)
    #     part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
    #     message.attach(part)
    

    # sending mail sever (leave as default)
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() 
            server.login(sender_mail, email_password) 
            
            server.sendmail(sender_mail, receiver_mails, message.as_string())
            print(f"=== Email sent successfully to: {', '.join(receiver_mails)} ===")
        
    except Exception as e:
        print(f'=== Unable to send mail {e} ===')


def get_crypto_data():
# Coingecko API information, you can change api to another website's api
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    param = {
        'vs_currency' : 'usd',
        'order' : 'market_cap_desc',
        'per_page': 250, #<-- fecthing only 250 rows, increase or decrease at will
        'page': 1 # <-- fetching data only from page 1, increase to 2,3,4 pages at will.
    }

    response = requests.get(url, params=param) # <-- sending requests to Api. (In order not to get your ip blocked by the api, run script max of once per 1 minute)
    # spamming multiple requests will get your ip blocked!.

    if response.status_code == 200: # <-- checking connection status (200 = connection succesful!)
        print("=== Connection Succesful!, Getting Data!... ===")

        data = response.json() # <-- storing response into data
        print('=== Data received! ===')

        df = pd.DataFrame(data) # <-- creating dataframe directly from a json data/file using pandas
        print('=== Created Dataframe ===')

        # print(df.columns) # <-- Exploring Data
        # print(df.head(10)) # <-- Exploring Data

        df = df[[  # <-- selecting needed columns. (explore columns, add more columns or remove from current at will)
            'id', 'symbol', 'name' ,'current_price', 'market_cap', 'price_change_percentage_24h',
            'ath', 'atl'
        ]]
        print('=== Selecting Columns ===')

        time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # <-- creating a new column with datetime information.
        df['time_stamp'] = time_stamp
        print('=== Created Timestamp! ===')

        """ use this block if you will rather download csv file to pc before attaching in mail
        """
        #saving the data to csv with pandas
        # df.to_csv(f'crypto_data {time_stamp}.csv', index=False)
        # print('==== Data Saved Successfully ====')

        csv_buffer = io.StringIO() # <-- this block is only creating CSV file in memory (rather than saving new file everytime you run script)
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)  # <-- rewind to start
        print('=== File created in memory! ===')

        filename = csv_buffer.getvalue() 
        #Storing the csv content in a "filename" variable. filename variable here is what's passed into send_mail function earlier, 
        #if you chnage variable name, update filename variable in send_mail function
        print('=== File stored in Filename variable ===')
        
        #getting today's date
        today = datetime.now().strftime('%Y-%m-%d')

        # getting bottom 10 crypto
        top_negative_10 = df.nsmallest(10, 'price_change_percentage_24h')
        
        # getting bottom 10 crypto
        top_positive_10 = df.nlargest(10, 'price_change_percentage_24h')

        #storing data to html for better formatting (to be used later in mail. (optional))
        top_negative_10_html = top_negative_10.to_html(index=False, justify='center', border=0)
        top_positive_10_html = top_positive_10.to_html(index=False, justify='center', border=0)
        

        # connecting with postgres (pass in your postgres credentials)
        # i'm pushing data to sql database rather than store as csv file loaclly
        try:
            conn = psycopg2.connect(
                host="",
                dbname ="",
                password="",
                user="",
                port="")
            
            conn.autocommit = True # <-- tells postgres to not start a transaction block and commit each query
            print('=== Succefully Connected With Postgres ===')
        except psycopg2.Error as e:
            print(f'Error connecting to postgres: {e}')

        #creating postgres cursor
        cur = conn.cursor()
        print('=== Cursor created succesfully ===')

        #Checking if database exists
        db_name = 'crypto_db' # <-- change to db_name of choice
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
        exists = cur.fetchone()

        if not exists:
            try:
                cur.execute(f"CREATE DATABASE {db_name};")
                print(f"=== Database {db_name} created successfully. ===") # <-- creates new database if not exist
            except Exception as e:
                print(f"=== Error creating database {db_name}: ===", e)
        else:
            print(f"=== Database {db_name} already exists, skipping creation. ===") # <-- skips if databse already exists


        cur.close()
        conn.close() # <-- closing postgres connection
        print('=== Create_db connection closed successfully! ===')

        # reconnecting with postgres to switch from master db to created db & create table
        # pass in credentials
        print('=== Reconnecting with db ===')
        try:
            conn = psycopg2.connect(
                host="",
                dbname = db_name,
                password="",
                user="",
                port="" )
            
            conn.autocommit = True
            print(f'=== Succefully connected with {db_name} ===')
        except psycopg2.Error as e:
            print(f'=== Error connecting to {db_name}: {e} ===')

        #reopen postgres cursor
        cur = conn.cursor()
        print('=== Cursor reopened succesfully ===')

        table_name = 'crypto_data' # <-- change table name at will

        #sql create table syntax (create table to match columns selected with pandas dataframe earlier in the script)
        create_table = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
        id VARCHAR(100),
        symbol VARCHAR(50),
        name VARCHAR(150),
        current_price DOUBLE PRECISION,
        market_cap DOUBLE PRECISION,
        price_change_percentage_24h DOUBLE PRECISION,
        ath DOUBLE PRECISION,
        atl DOUBLE PRECISION,
        time_stamp TIMESTAMP
        );
        """

        #creating table
        try:
            cur.execute(create_table)
            print('=== Succesfully Created Table! ===')
        except Exception as e:
            print('=== Error creating table: ===', e)

        # Creating SQLAlchemy Engine to connect with PostgreSQL
        try:

            engine = create_engine(f'postgresql+psycopg2://postgres:@localhost:5432/{db_name}') # <-- pass in postgres password just after "..postgres:"
            print(f'=== Successfully created SQLAlchemy engine for {db_name} ===')
        except:
            print(f'=== Error creating SQLAlchemy engine engine for {db_name} ===')


        # Insert Data from DataFrame to PostgreSQL Table
        try:
            # sql query to check if today's data already exists.this block ensures you can run script multiple times without having duplicates for same day
            # if today's data aleready exist in databse, clear and insert fresh data. (modify query as you wish to fit your use case)
            with engine.connect() as check_conn:
                result = check_conn.execute(
                    text(f"SELECT COUNT(*) FROM {table_name} WHERE DATE(time_stamp) = :today"),
                    {"today": today}
                )
                today_count = result.scalar() # <-- .scalar() here returns just one row

            if today_count > 0:
                print(f"=== Found {today_count} records for {today}. Deleting old data for today ===")
                
                # Delete only today's records
                with engine.begin() as del_conn:
                    del_conn.execute(
                        text(f"DELETE FROM {table_name} WHERE DATE(time_stamp) = :today"),
                        {"today": today}
                    )
                print("=== Old records for today deleted. Now inserting fresh data... ===")

            # Append new (fresh) data
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists='append',
                index=False
            )
            print(f"=== New data inserted for {today}. ===")

        except Exception as e:
            print(f"=== Error inserting or updating data: {e} ===")

        # Close connections
        cur.close()
        conn.close()
        print("=== Cursor connections closed. ===")


        # call email function created earlier
        #email body is created using 'html' created earlier, mail body written using html code chatgpt generated for better formatting, 
        # preferably leave as default, if it breaks, i do not know html Lol!, so leave as default!
        subject = f"ETL Project (Top 10 crypto currency data to invest for {today})"

        style = """
            <style>
            body {
                font-family: Arial, sans-serif;
                color: #222;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f8f9fa;
            }
            h2 {
                color: #1a73e8;
                margin-bottom: 8px;
            }
            p {
                font-size: 15px;
                color: #333;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 10px;
                margin-bottom: 30px;
                font-size: 14px;
            }
            th, td {
                border: 1px solid #ddd;
                text-align: center;
                padding: 8px;
            }
            th {
                background-color: #eaf1fb;
                color: #222;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            .footer {
                font-size: 13px;
                color: #666;
                margin-top: 30px;
            }
            </style>
            """

        body = f"""
            <html>
            <head>{style}</head>
            <body>
                <h2>Good Morning! ☀️</h2>
                <p>Your CoinGecko crypto report is here!</p>

                <p>
                The CoinGecko crypto data for <strong>{today}</strong> has been successfully pulled from the CoinGecko API
                and appended to your <strong>PostgreSQL database</strong> for analysis.
                Attached is a full CSV snapshot for your crypto records, and below is a quick summary of today’s market movements.
                </p>

                <h2>📈 Top 10 Cryptos with Highest Price Increase (24h)</h2>
                {top_positive_10_html}

                <h2>📉 Top 10 Cryptos with Highest Price Decrease (24h)</h2>
                {top_negative_10_html}

                <div class="footer">
                <p>Best regards,</p>
                <p><strong>Oluwatosin Amosu,</strong><br> 
                    Senior Data Analyst,<br>
                    Baby Data Engineer
                </p>
                
                <br> <!-- spacing -->
                
                <p>
                    <em>Tbrown's Automated Python ETL Project</em><br>
                    This is an automated email, please do not reply!.<br>
                    See you tomorrow!
                </p>
                </div> 
                </body> 
                </html> """

        # <-- my initial ail body before rewritting with chatgpt html, Lol.

        # body = f"""
        # Good Morning!\n\n
        
        # Your coin gecko crypto report is here!\n\n

        # The coin gecko crypto data for {today} has been pulled from coin gecko api and successfully appended to your PostgreSQL db for query.
        # Attached is a snapshot for your crypto records, also attached is the full csv data for {today} \n\n\n
        
        # Top 10 crypto with highest price increase in last 24 hour!\n
        # {top_positive_10_html}\n\n\n
        
        
        # Top 10 crypto with highest price decrease in last 24 hour!\n
        # {top_negative_10_html}\n\n\n
        
        # Regards!\n
        # This an automated etl python project, do not respond to this mail!\n
        # See you same time tomorrow, bye!. 
        # Your crypto python application.    
        # """
        
        # sending mail
        send_mail(subject, body, filename, today) # <-- update filename variable here, if you changed it earlier in the script

        print('=== mail sent successfully! ===')
    else:
        print(f"Connection Failed for Error Code{response.status_code}")

# this get executed only if we run this function
if __name__ == '__main__':

    # call the function
    # get_crypto_data() # <-- uncomment to run file directly

    schedule.every().day.at('09:00').do(get_crypto_data()) # <-- set to preferred time

    while True:
        schedule.run_pending() # <-- script only runs if file is open and running, comment out this block and the schedule block above to run file immediately.

# Thanks for getting to the bottom of my code, Ciao!, Tbrown!