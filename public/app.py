import os
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app, db

# Initialize Flask app
app = Flask(__name__)

# Initialize Firestore DB
default_app = initialize_app()
db = firestore.client()

@app.route("/")
def index():
    return "Virtual Pet Calendar"