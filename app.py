# Main Flask app -- import grocery module

from flask import Flask, redirect, url_for, render_template
import datetime

## Database handling stuff
import core.database
from modules.groceries import models as grocery_models

## Set up all database schema
grocery_models.setup_schema()

# Display current time on splash screen
current_time = datetime.datetime.now()
time_display = current_time.strftime("%H:%M:%S")
date_display = current_time.strftime("%A, %B %d")

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", time_display=time_display, date_display=date_display)

@app.route("/grocery")
def grocery():
    return render_template("barcode_scanner/grocery.html")

@app.route("/add_product")
def add_product():
    return render_template("barcode_scanner/add.product.html")

if __name__ == "__main__":
    app.run()