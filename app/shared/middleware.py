from flask import session

def set_toast(message: str, type: str = "info") -> None:
    session['toast'] = {"message": message, "type": type}