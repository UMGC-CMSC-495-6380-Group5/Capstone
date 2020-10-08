#DATE           TEAM MEMBER         UPDATE
#10/08/2020     NCROWN              Created tuplebuilder.py to handle building of queries and tuples for newaccount

def outputTuple(firstName, lastName, phone, instructor, birthdate, belt, userStatus, email, parent, notes, address, username, password):
    queryTuple = (firstName, lastName, phone, instructor, birthdate, belt, userStatus)
    if email != '':
        queryTuple = queryTuple + (email,)
    if parent != None:
        queryTuple = queryTuple + (parent,)
    if notes != '':
        queryTuple = queryTuple + (notes,)
    if address != '':
        queryTuple = queryTuple + (address,)
    if username != None:
        queryTuple = queryTuple + (username,)
    if password != None:
        queryTuple = queryTuple + (password,)
    return queryTuple

def outputQuery(firstName, lastName, phone, instructor, birthdate, belt, userStatus, email, parent, notes, address, username, password):
    queryStart = "INSERT INTO Accounts (First_Name, Last_Name, Phone, Instructor, DOB, Belt, Status"
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
        queryValues += ", %s"
    #final query construction
    query = queryStart+queryValues+queryEnd 
    return query

def outputBelt(beltDB):
    belt = ''
    if beltDB == "1":
        belt = 1
    elif beltDB == "2":
        belt = 2
    elif beltDB == "3":
        belt = 3
    elif beltDB == "4":
        belt = 4
    elif beltDB == "5":
        belt = 5
    elif beltDB == "6":
        belt = 6
    elif beltDB == "7":
        belt = 7
    elif beltDB == "8":
        belt = 8
    elif beltDB == "9":
        belt = 9
    elif beltDB == "10":
        belt = 10
    elif beltDB == "11":
        belt = 11
    elif beltDB == "12":
        belt = 12
    elif beltDB == "13":
        belt = 13
    elif beltDB == "14":
        belt = 14
    elif beltDB == "15":
        belt = 15
    elif beltDB == "16":
        belt = 16
    elif beltDB == "17":
        belt = 17
    return belt