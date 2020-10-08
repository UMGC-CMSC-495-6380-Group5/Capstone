#DATE           TEAM MEMBER         UPDATE
#09/24/2020     DROBERTS            Created application.py frame
#10/03/2020     NCROWN              Created authenticate() function for login
#10/04/2020     NCROWN              Updated functionality of authenticate() to connect to database and compare hashed passwords
#10/04/2020     TFEITOSA            Created newclass() function for newclass interface
#10/05/2020     NCROWN              Updated application to handle sessions, removed demo code, and added logout function
#10/05/2020     DROBERTS            Changed application to run with new SSL certificates
#10/05/2020     NCROWN              Added addaccount, Added sessioncount function and related code to login function to prevent excessive login attempts
#10/05/2020     TFEITOSA            Created show_calendar() function for the calendar interface
#10/06/2020     NCROWN              Added error handling for database connection error to authenticate(); Added form support for newaccount; implemented passHash() and DisconnectDB(); added backend for confirm.html
#10/07/2020     NCROWN              Fixed errors on backend of confirm() function for passing empty tuples by using global variables
#10/07/2020     NCROWN              Implemented tuplebuilder functions; continued development on confirm() function
#10/08/2020     NCROWN              Implemented SHA256 password encryption, completed confirm()/newaccount() functionality; updated newclass to interact with confirm() functionality; completed newclass() functionality

from flask import Flask, render_template, request, session, redirect, url_for, flash
#from testform import TestForm
from app_calendar import *
from database_connector import ConnectDB, DisconnectDB
from datetime import timedelta, date
from passwordhashgen import passHash, passCompare
from tuplebuilder import accountTuple, outputBelt, accountQuery, timeBuilder

#global variables to mitigate issue with passing queries and tuples to confirm()
query = ''
queryTuple = ''

#flask framework
app = Flask(__name__)
app.config['SECRET_KEY'] ='12345'

#Session handling
@app.route('/', methods=['get'])
def sessioncount():
    #Sets lifetime of session to 5 minutes for login attempts
    if "instructor" in session:
        return redirect(url_for('show_calendar'))
    else:
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=5)
        #If no attempt session is active, creates the session
        if "attempt" not in session:
            session['attempt'] = 0
    return redirect(url_for('authenticate'))

#Login handling    
@app.route('/login', methods=['post', 'get'])
def authenticate():
    message = ''
    error = ''
    #Handles if the user navigated directly to login and didn't set a sessioncount
    if "attempt" not in session:
        return redirect(url_for('sessioncount'))
    #Correct path
    else:
        if request.method == 'POST':
            #Blocks user from excessive login attempts
            if session['attempt'] >= 3:
                message = "Too many failed attempts. Please wait 5 minutes."
            #Correct path
            else:
                #Imports form data from index.html
                username = request.form.get('formuser') 
                userpass = request.form.get('formpass')
                #Connecting to the database
                try:
                    mydb = ConnectDB()
                    #Queries the database for credentials
                    mycursor = mydb.cursor()
                    mycursor.execute("SELECT PassHash FROM Accounts WHERE Username = %s", (username,))
                    result = mycursor.fetchone()
                    #Checks for results
                    if result is None:
                        message = "Incorrect username or password"
                        attempt = session.get('attempt')
                        attempt += 1
                        session['attempt']=attempt
                    #Compares hashed passwords
                    else:
                        #Correct path
                        importHash = ''.join(result)
                        passwordCompare = False
                        passwordCompare = passCompare(userpass, importHash)
                        if passwordCompare == True:
                            message = "Correct credentials"
                            #Creates session with username
                            app.permanent_session_lifetime = timedelta(minutes=15)
                            session['instructor'] = username
                            session.pop('attempt', None)
                            return redirect(url_for('show_calendar'))           
                        #Incorrect credentials
                        else:
                            message = "Incorrect username or password"
                            attempt = session.get('attempt')
                            attempt += 1
                            session['attempt']=attempt
                #Database connection failure
                except:
                    error = "Database error"
        #Handles session already being active
        else:
            if "instructor" in session:
                return redirect(url_for('show_calendar'))
            
    return render_template('login.html', message=message, error=error)

#Handles logging the user out
@app.route('/logout')
def logout():
    #Kills the user session, logging them out
    session.pop('instructor', None)
    return redirect(url_for('sessioncount'))

#Handles the calendar
@app.route('/calendar')
def show_calendar():
    #active session
    
    if "instructor" in session:

        y = get_year()
        m = get_month()
        mn = get_month_name()
        d = get_day()
        dm = get_days_in_month()
        wd = get_first_weekday()
        t = get_total_accounts()
        ac = get_all_classes_TESTING()
        
    #bad session
    else:
        return redirect(url_for('sessioncount'))
    return render_template('calendar.html', year=y, month=m, day=d, days_in_month=dm,
    weekday=wd, month_name=mn, total_accounts=t, all_classes=ac)

#Handles creation of new accounts    
@app.route('/newaccount', methods = ['GET', 'POST'])
def newaccount():
    error = ''
    #active session
    if "instructor" in session:
        try: 
            mydb = ConnectDB()
            mycursor = mydb.cursor()
            #Populates belt selection dropdown
            mycursor.execute("SELECT * FROM BeltRanks order by BeltID")
            beltList = mycursor.fetchall()
            if request.method == 'POST':
                #Imports form data from newaccount.html
                firstName = request.form.get('first_name')
                lastName = request.form.get('last_name')
                address = request.form.get('address') 
                phone = request.form.get('phone')
                email = request.form.get('email') 
                birthdate = request.form.get('birthday')
                parent = request.form.get('parent') 
                notes = request.form.get('notes')
                beltDB = request.form.get('belt')
                instructor = request.form.get('instructor') 
                username = request.form.get('username')
                password = request.form.get('password')
                #Sets boolean/integer values
                userStatus = 1
                #Handles instructor checkbox value and rogue username/password entry
                if instructor == None:
                    instructor = 0
                    username = None
                    password = None
                else:
                    instructor = 1
                    password = passHash(password)
                #Converts beltDB string to int
                belt = outputBelt(beltDB)
                #Query tuple constuction
                global queryTuple
                queryTuple = accountTuple(firstName, lastName, phone, instructor, birthdate, belt, userStatus, email, parent, notes, address, username, password)
                #final query construction
                global query
                query = accountQuery(firstName, lastName, phone, instructor, birthdate, belt, userStatus, email, parent, notes, address, username, password)
                #Checks Accounts for anyone with the same last name
                mycursor.execute("SELECT First_Name FROM Accounts WHERE Last_Name = %s", (lastName,))
                result = mycursor.fetchall()
                #Compares query results to current form data
                if result is None:
                    #Submits data into database
                    mycursor.execute(query, queryTuple)
                    mydb.commit()
                    #Flash message passed to next page load
                    flash('Record added.', 'succes')
                    #Clear globals
                    query = ''
                    queryTuple = ''
                    return redirect(url_for('newaccount'))
                #Last name found in database
                else:
                    #First name found in database, asks user to confirm creation of new account
                    if (any(firstName in i for i in result)):
                        #Builds name string
                        name = firstName + ' ' + lastName
                        #redirect to confirm() with variables
                        return redirect(url_for('confirm', name=name, page='newaccount'))
                    #Unique name
                    else:
                        #submits data into database
                        mycursor.execute(query, queryTuple)
                        mydb.commit()
                        #Flash message passed to next page load
                        flash('Record added.', 'succes')
                        #Clear globals
                        query = ''
                        queryTuple = ''
                        return redirect(url_for('newaccount'))
        except:
                error = 'Database error'
    #bad session
    else:
        return redirect(url_for('sessioncount'))
    return render_template('newaccount.html', beltList=beltList, error=error)
    
#Confirmation handling
@app.route('/confirm/<name>/<page>', methods = ['GET', 'POST'])
def confirm(name, page):
    #Calls global query
    confirmQuery = globals()['query']
    error = ''
    #Session good
    if "instructor" in session:
        #If the query is empty, redirects back to the calendar
        if confirmQuery == None:
            redirect(url_for('show_calendar'))
        #Good path
        else:
            #Get global queryTuple
            confirmQueryTuple = globals()['queryTuple']
            #Good path
            try:
                mydb = ConnectDB()
                mycursor = mydb.cursor()
                #Constructs message for display on the confirm.html page
                message = 'There is already a database entry for ' + name + ". Do you wish to create a new record anyway?"
                #Button press
                if request.method == 'POST':
                    #Calls globals for clearing
                    global query
                    global queryTuple
                    #Handles confim button
                    if 'confirmbutton' in request.form:
                        #Insert query/tuple into database
                        mycursor.execute(confirmQuery, confirmQueryTuple)
                        mydb.commit()
                        #Pass flash message to next page
                        flash('Record added.', 'succes')
                        #Reset globals
                        query = ''
                        queryTuple = ''
                        return redirect(url_for(page))
                    #Handles deny button
                    elif 'denybutton' in request.form:
                        #Pass flash message to next page
                        flash('Canclled record upload.', 'succes') 
                        #Reset globals
                        query = ''
                        queryTuple = ''
                        return redirect(url_for(page))
            #Handles errors
            except:
                error = 'Database error'
    #Session bad
    else:
        return redirect(url_for('sessioncount'))
    return render_template('confirm.html', message=message, error=error, name=name, page=page)

#Handles creation of new classes
@app.route('/newclass', methods = ['GET', 'POST'])
def newclass():
    #Session good
    if "instructor" in session:
        error = ''
        #Build lists for select options in newclass.html
        hourList = ["00", "01", "02", "03", "04" , "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]
        minuteList = ["00", "15", "30", "45"]
        if request.method == "POST":
            #Get values from newclass.html form
            class_name = request.form.get('class_name')
            date = request.form.get('date')
            start_hour = request.form.get('starthour')
            end_hour = request.form.get('endhour')
            start_minute = request.form.get('startminute')
            end_minute = request.form.get('endminute')
            
            #Send times to timeBuilder to construct time strings
            start_time = timeBuilder(start_hour, start_minute)
            end_time = timeBuilder(end_hour, end_minute)
            
            #Update query and queryTuple global variables to facilitate confirm()
            global query
            query = "INSERT INTO Classes (ClassName, ClassDate, ClassStartTime, ClassEndTime) VALUES (%s, %s, %s, %s)"
            global queryTuple
            queryTuple = (class_name, date, start_time, end_time)
            
            #Good path
            try: 
                mydb = ConnectDB()
                mycursor = mydb.cursor()
                #Query database to see if class exists in this time/date slot
                mycursor.execute("SELECT ClassStartTime FROM Classes WHERE ClassDate = %s", (date,))
                result = mycursor.fetchall()
                #Compares query results to current form data
                if result is None:
                    #Submits data into database
                    mycursor.execute(query, queryTuple)
                    mydb.commit()
                    #Flash message for next page laod
                    flash('Record added.', 'succes')
                    #Clear globals
                    query = ''
                    queryTuple = ''
                    return redirect(url_for('newclass'))
                #Date found in database
                else:
                    #Time and date found in database, asks user to confirm creation of new class
                    if (any(start_time in i for i in result)):
                        #Builds name string
                        name = "class starting at " + start_time + " on " + date
                        #Redirects to confirm() with variables
                        return redirect(url_for('confirm', name=name, page='newclass'))
                    #Unique class
                    else:
                        #Submits data into database
                        mycursor.execute(query, queryTuple)
                        mydb.commit()
                        #Flash message for next page load
                        flash('Record added.', 'succes')
                        #Clear globals
                        query = ''
                        queryTuple = ''
                        return redirect(url_for('newaccount'))
            #Handles errors
            except:
                error = 'Database error'
    #Session bad
    else:
        return redirect(url_for('sessioncount'))
    
    return render_template('newclass.html', error=error, hourList=hourList, minuteList=minuteList)
    
#flask framework
app.run(ssl_context='adhoc', host='0.0.0.0', port=8080)