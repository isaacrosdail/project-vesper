from flask import session

def set_toast(message: str, type: str = "info") -> None:
    """
    Queues a toast for display after redirect.
    JS reads from `data-toast` on body (base.html) and displays it.
    """
    session['toast'] = {"message": message, "type": type}