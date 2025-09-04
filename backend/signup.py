#!/usr/bin/env python3
from models import User, login, session
import cgi
import cgitb; cgitb.enable()

form = cgi.FieldStorage()
email = form.getvalue("email")
password = form.getvalue("password")

if email and password:
    if login(email, password):
        print("Content-Type: text/html\n")
        print("<html><body><h1>Login Successful!</h1><p>Welcome to My Desire Salon!</p></body></html>")
    else:
        print("Content-Type: text/html\n")
        print("<html><body><h1>Login Failed!</h1><p><a href='/login.html'>Try Again</a></p></body></html>")
else:
    print("Content-Type: text/html\n")
    print("<html><body><h1>Invalid Input!</h1><p><a href='/login.html'>Try Again</a></p></body></html>")

session.close()

