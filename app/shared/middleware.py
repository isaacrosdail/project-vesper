from flask import session


def set_toast(message: str, toast_type: str = "info") -> None:
    """
    Queues a toast for display after redirect.
    JS reads from `data-toast` on body (base.html) and displays it.

    Options for toast_type: `error`, `success`, `info`, `warning` (default: `info`)
    """
    session["toast"] = {"message": message, "type": toast_type}
