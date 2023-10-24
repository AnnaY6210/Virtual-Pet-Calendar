import os
from flask import Flask, request, jsonify, redirect, url_for, render_template
from firebase_admin import credentials, firestore, initialize_app, db

# Initialize Flask app
app = Flask(__name__)

# Initialize Firestore DB
default_app = initialize_app()
db = firestore.client()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/hello_world")
def hello_world():
    return render_template("hello.html", content="virtual pet calendar")

@app.route("/inv")
def inventory():
    return render_template("inventory.html")



if __name__ == "__main__":
    app.run()
