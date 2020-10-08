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

from flask import Flask, render_template, request, session, redirect, url_for, flash
#from testform import TestForm
from app_calendar import *
from database_connector import ConnectDB, DisconnectDB
from datetime import timedelta
from datetime import date
from passwordhashgen import passHash
from tuplebuilder import outputTuple, outputBelt, outputQuery

#global variables
firstName = ''
lastName = ''
phone = ''
instructor = ''
birthdate = ''
belt = 1
userStatus = 1
email = ''
parent = ''
notes = ''
address = ''
username = ''
password = ''
instructor = 0
query = ''

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
                #Password/salt hash conversion
                suppliedHash = passHash(userpass)
                #Connecting to the database
                try:
                    mydb = ConnectDB()
                    #Queries the database for credentials
                    mycursor = mydb.cursor()
                    mycursor.execute("SELECT PassHash FROM Accounts WHERE Username = %s", (username,))
                    result = mycursor.fetchone()
                    DisconnectDB(mycursor, mydb)
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
                        if importHash == suppliedHash:
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
    message = ''
    error = ''
    #active session
    if "instructor" in session:

        mydb = ConnectDB()
        mycursor = mydb.cursor()
        #Populates belt selection dropdown
        mycursor.execute("SELECT * FROM BeltRanks order by BeltID")
        beltList = mycursor.fetchall()
        #DisconnectDB(mycursor, mydb)
        if request.method == 'POST':
            #Imports form data from newaccount.html
            global firstName
            firstName = request.form.get('first_name')
            global lastName
            lastName = request.form.get('last_name')
            global address
            address = request.form.get('address') 
            global phone
            phone = request.form.get('phone')
            global email
            email = request.form.get('email') 
            global birthdate
            birthdate = request.form.get('birthday')
            global parent
            parent = request.form.get('parent') 
            global notes
            notes = request.form.get('notes')
            beltDB = request.form.get('belt')
            instructorInput = request.form.get('instructor') 
            global username
            username = request.form.get('username')
            global password
            password = request.form.get('password')
            #Sets boolean values
            global userStatus
            userStatus = 1
            if instructorInput == None:
                instructorInput = 0
            else:
                instructorInput = 1
            global instructor
            instructor = instructorInput
            #Base query constuction
            global belt
            belt = outputBelt(beltDB)
            queryTuple = outputTuple(firstName, lastName, phone, instructor, birthdate, belt, userStatus, email, parent, notes, address, username, password)
            '''queryStart = "INSERT INTO Accounts (First_Name, Last_Name, Phone, Instructor, DOB, Belt, Status"
            queryValues = ") VALUES (%s, %s, %s, %s, %s, %s, %s"
            queryEnd = ")"
            #Query building
            if email != '':
                queryStart += ", Email"
                queryValues += ", %s"
            if parent != None:
                queryStart += ", Parent"
                queryValues += ", %s"
            if notes != '':
                queryStart += ", Notes"
                queryValues += ", %s"
            if address != '':
                queryStart += ", Address"
                queryValues += ", %s"
            if username != None:
                queryStart += ", Username"
                queryValues += ", %s"
            if password != None:
                queryStart += ", PassHash"
                queryValues += ", %s"'''
            #final query construction
            global query
            query = outputQuery(firstName, lastName, phone, instructor, birthdate, belt, userStatus, email, parent, notes, address, username, password)
            #query = queryStart+queryValues+queryEnd
            #Checks Accounts for anyone with the same last name
            mycursor.execute("SELECT First_Name FROM Accounts WHERE Last_Name = %s", (lastName,))
            result = mycursor.fetchall()
            #Compares query results to current form data
            if result is None:
                mycursor.execute(query, queryTuple)
                mydb.commit()
                flash('Record added.', 'succes')
                return redirect(url_for('newaccount'))
            #Last name found in database
            else:
                #First name found in database, asks user to confirm creation of new account
                if (any(firstName in i for i in result)):
                    name = firstName + ' ' + lastName
                    #DisconnectDB(mycursor, mydb)
                    return redirect(url_for('confirm', name=name, page='newaccount'))
                #Unique name
                else:
                    mycursor.execute(query, queryTuple)
                    mydb.commit()
                    flash('Record added.', 'succes')
                    return redirect(url_for('newaccount'))
                    #DisconnectDB(mycursor, mydb)
    #bad session
    else:
        return redirect(url_for('sessioncount'))
    return render_template('newaccount.html', beltList=beltList, message=message, error=error)
    
#Confirmation handling
@app.route('/confirm/<name>/<page>', methods = ['GET', 'POST'])
def confirm(name, page):
    #global query
    confirmQuery = globals()['query']
    error = ''
    #Session good
    if "instructor" in session:
        #redirect
        if confirmQuery == None:
            redirect(url_for('show_calendar'))
        #Session good
        else:
            if page == "newaccount":
                confirmFirstName = globals()['firstName']
                confirmLastName = globals()['lastName']
                confirmAddress = globals()['address']
                confirmPhone = globals()['phone']
                confirmEmail = globals()['email']
                confirmBirthdate = globals()['birthdate']
                confirmParent = globals()['parent']
                confirmNotes = globals()['notes']
                confirmBelt = globals()['belt']
                confirmUserStatus = globals()['userStatus']
                confirmInstructor = globals()['instructor']
                confirmUsername = globals()['username']
                confirmPassword = globals()['password']
                #queryTuple = (confirmFirstName, confirmLastName, confirmPhone, confirmInstructor, confirmBirthdate, confirmBelt, confirmUserStatus)
                queryTuple = outputTuple(confirmFirstName, confirmLastName, confirmPhone, confirmInstructor, confirmBirthdate, confirmBelt, confirmUserStatus, confirmEmail, confirmParent, confirmNotes, confirmAddress, confirmUsername, confirmPassword)
            try:
                mydb = ConnectDB()
                mycursor = mydb.cursor()
                message = 'There is already a database entry for ' + name + ". Do you wish to create a new record anyway?"
                if request.method == 'POST':
                    if 'confirmbutton' in request.form:
                        print(confirmQuery)
                        print(queryTuple)
                        mycursor.execute(confirmQuery, queryTuple)
                        mydb.commit()
                        flash('Record added.', 'succes') 
                        return redirect(url_for(page))
                    elif 'denybutton' in request.form:
                        flash('Canclled record upload.', 'succes') 
                        return redirect(url_for(page))
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
        message = ""
        if request.method == "POST":
            class_name = request.form('class_name')
            date = request.form('date')
            start_time = request.form('start_time')
            end_time = request.form('end_time')
            students = request.form('students')
            instructors = request.form('instructors')
            
            query = "INSERT INTO Classes (ClassName, ClassDate, ClassStartTime, ClassEndTime) VALUES"
            query += "(" + class_name + "," + date + "," + start_time + "," + end_time + ");"
            
            try: 
                mydb = ConnectDB()
                conn = mydb.cursor()
                conn.execute(query)
                message = "Class Recorded"
            except OSError:
                message = "Unable to save class"
    #Session bad
    else:
        return redirect(url_for('sessioncount'))
    
    return render_template('newclass.html', message=message)
    

app.run(ssl_context='adhoc', host='0.0.0.0', port=8080)
