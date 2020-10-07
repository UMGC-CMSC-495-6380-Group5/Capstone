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

from flask import Flask, render_template, request, session, redirect, url_for
#from testform import TestForm
from app_calendar import *
from database_connector import ConnectDB, DisconnectDB
from datetime import timedelta
from datetime import date
from passwordhashgen import passHash

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
            firstName = request.form.get('first_name') 
            lastName = request.form.get('last_name')
            address = request.form.get('address') 
            phone = request.form.get('phone')
            email = request.form.get('email') 
            birthdate = request.form.get('birthday')
            parent = request.form.get('parent') 
            notes = request.form.get('notes')
            belt = request.form.get('belt')
            instructor = request.form.get('instructor') 
            username = request.form.get('username')
            password = request.form.get('password')
            userStatus = 1
            if instructor == None:
                instructor = 0
            else:
                instructor = 1
            queryTuple = firstName, lastName, phone, instructor, birthdate, int(belt), userStatus
            queryStart = "INSERT INTO Accounts (First_Name, Last_Name, Phone, Instructor, DOB, Belt, Status"
            queryValues = ") VALUES (%s, %s, %s, %s, %s, %s, %s"
            queryEnd = ")"
            ############Test Code
            if email != '':
                queryTuple = queryTuple + (email,)
                queryStart += ", Email"
                queryValues += ", '%s'"
            if parent != None:
                queryTuple = queryTuple + (parent,)
                queryStart += ", Parent"
                queryValues += ", '%s'"
            if notes != '':
                queryTuple = queryTuple + (notes,)
                queryStart += ", Notes"
                queryValues += ", '%s'"
            if address != '':
                queryTuple = queryTuple + (address,)
                queryStart += ", Address"
                queryValues += ", '%s'"
            if username != None:
                queryTuple = queryTuple + (username,)
                queryStart += ", Username"
                queryValues += ", '%s'"
            if password != None:
                queryTuple = queryTuple + (password,)
                queryStart += ", PassHash"
                queryValues += ", '%s'"
            query = queryStart+queryValues+queryEnd
            
            #queryTuple += queryEnd
            #message = (firstName + ', ' + lastName + ', ' + address + ', ' + phone + ', ' + email  + ', ' + birthdate + ', ' + parent + ', ' + notes + ', ' + belt + ', ' + instructor + ', ' + username + ', ' + password)
            #########Test Code End
            # Checks Accounts for anyone with the same last name
            #mydb = ConnectDB()
            #mycursor = mydb.cursor()
            mycursor.execute("SELECT First_Name FROM Accounts WHERE Last_Name = %s", (lastName,))
            result = mycursor.fetchall()
            #query = """INSERT INTO Accounts (First_Name, Last_Name, Address, Phone, Email, DOB, Parent, Status, Notes, Belt, Instructor, Username, PassHash) VALUES (%s, %s, %s, %s, %s, %s, %s, %i, %s, %i, %i, %s, %s)"""
            #queryTuple = (firstName, lastName, address, phone, email, birthdate, parent, userStatus, notes, belt, instructor, username, password)
            print(query)
            print(queryTuple)
            if firstName in result:
                name = firstName + ' ' + lastName
                #DisconnectDB(mycursor, mydb)
                return redirect(url_for(confirm(query, queryTuple, name)))
            else:
                mycursor.execute(query, queryTuple)
                mydb.commit()
                #DisconnectDB(mycursor, mydb)
    #bad session
    else:
        return redirect(url_for('sessioncount'))
    return render_template('newaccount.html', beltList=beltList, message=message, error=error)
    
#Confirmation handling
@app.route('/confirm', methods = ['GET', 'POST'])
def confirm(query, queryTuple, name):
    #Session good
    error = ''
    if "instructor" in session:
        if query == None:
            redirect(url_for('show_calendar'))
        else:
            try:
                mydb = ConnectDB()
                mycursor = mydb.cursor()
                message = 'There is already a database entry for ' + name + ". Do you wish to create a new record anyway?"
                if form.validate_on_submit():
                    if 'confirmbutton' in request.form:
                        mycursor.execute(query, queryTuple)
                        return redirect(url_for('show_calendar'))
                    elif 'denybutton' in request.form:
                        return redirect(url_for('show_calendar'))
            except:
                error = 'Database error'
    #Session bad
    else:
        return redirect(url_for('sessioncount'))
    return render_template('confirm.html', message=message, error=error)

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
