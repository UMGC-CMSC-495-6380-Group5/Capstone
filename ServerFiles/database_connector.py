#DATE           TEAM MEMBER         UPDATE
#09/24/2020     DROBERTS            Created database_connector.py
#10/04/2020     NCROWN              Updated code to be callable as an imported function and commented out example code

import mysql.connector

#Connecting to the database
def ConnectDB():
    mydb = mysql.connector.connect(
        host ="oyd-database.ckc4mk1cvfc5.us-east-1.rds.amazonaws.com",
        user="admin",
        password="Group5RDS",
        database="StudentDatabase"
        )
    return mydb
#Example of executing a parameterized call
#mycursor = mydb.cursor()
#mycursor.execute("CREATE DATABASE %s" % ("StudentDatabase"))
