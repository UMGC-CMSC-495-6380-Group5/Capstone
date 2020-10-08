#DATE 			TEAM MEMBER     UPDATE
#09/29/2020     NCROWN          Created passwordhashgen.py file
#10/06/2020     NCROWN          Updated passwordhashgen.py to be a callable function
#10/08/2020     NCROWN          Added passCompare() function and implemented passlib password encryption
import hashlib
from passlib.hash import sha256_crypt

def passHash(inputPassword):
    salt = "salt"
    db_password = inputPassword+salt
    h = sha256_crypt.encrypt(db_password)
    return h

def passCompare(inputPassword, dbHash):
    salt = "salt"
    inputPass = inputPassword+salt
    dbPassresult = sha256_crypt.verify(inputPass, dbHash)
    return dbPassresult