from flask import session

def set_toast(message, type = "info"):
    session['toast'] = {"message": message, "type": type}