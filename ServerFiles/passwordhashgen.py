#DATE 			TEAM MEMBER     UPDATE
#09/29/2020     NCROWN          Created passwordhashgen.py file
#10/06/2020     NCROWN          Updated passwordhashgen.py to be a callable function
import hashlib

def passHash(inputPassword):
    salt = "salt"
    db_password = inputPassword+salt
    h = hashlib.md5(db_password.encode())
    return h.hexdigest()