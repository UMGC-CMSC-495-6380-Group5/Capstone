#DATE           TEAM MEMBER         UPDATE
#10/05/2020     TFEITOSA            Created app_calendar.py
#10/03/2020     NCROWN              Updated to include revision table

from datetime import date
from database_connector import ConnectDB
import calendar

mydb = ConnectDB()
today = date.today()

def get_year():
    year = int(today.strftime("%y"))
    year += 2000
    return year
    
def get_month():
    month = int(today.strftime("%m"))
    return month

def get_month_name():
    month_name = today.strftime("%B")
    return month_name

def get_day():
    day = int(today.strftime("%d"))
    return day
    
def is_leap_year():
    year = int(today.strftime("%y"))
    year += 2000
    return calendar.isleap(year)
        
def get_days_in_month():
    month = int(today.strftime("%m"))
    year = int(today.strftime("%y"))
    year += 2000
    jmm = [1,3,5,7,8,10,12]
    ajs = [4,6,9,11]
    if month in jmm:
        return 31
    elif month in ajs:
        return 30
    else:
        if is_leap_year():
            return 29
        else:
            return 28
            
def get_first_weekday():
    firstday = calendar.weekday(2020, 10, 1)
    return firstday
    
def get_total_accounts():
    query = "SELECT COUNT(*) FROM Accounts;"
    try: 
        mydb = ConnectDB()
        conn = mydb.cursor()
        conn.execute(query)
        result = conn.fetchone()
    except OSError:
        result = "Error Total"
    number = result[0]
    return number
    
def get_all_classes_TESTING():
    query = "SELECT * FROM Classes"
    try: 
        mydb = ConnectDB()
        conn = mydb.cursor()
        conn.execute(query)
        result = conn.fetchall()
    except OSError:
        result = "Error Total"
    return result

def do_query():
    query = "TYPE acctlist IS VARRAY(99) OF NUMBER;"
    try:
        mydb = ConnectDB()
        conn = mydb.cursor()
        conn.execute(query)
    except OSError:
        result = "Error"
        
    