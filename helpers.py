import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
import sqlite3
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def convert(time):
    char = 0
    while time[char] != ":":
        char = char + 1

    if char == 1:
        time = time + " " + "A.M."
    else:
        hour = time[0] + time[1]
        if hour == "12":
            time = time + " " + "P.M."
        elif hour == "00":
            hour  = str(12)
            time = hour + ":" + time[3] + time[4] + " " + "A.M."
        elif int(hour) > 12:
            hour = str(int(hour) - 12)
            if hour == "12":
                time = hour + ":" + time[3] + time[4] + " " + "A.M."
            else:
                time = hour + ":" + time[3] + time[4] + " " + "P.M."
        else:
            time = time + " " + "A.M."
    return time 


   

