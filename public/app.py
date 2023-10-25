import os, flask, sys, httplib2
from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from firebase_admin import credentials, firestore, initialize_app, db
from oauth2client import client
from googleapiclient import discovery

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "password"

# Initialize Firestore DB
default_app = initialize_app()
db = firestore.client()


@app.route("/")
def index():
    if "credentials" not in session:
        return redirect(url_for("oauth2callback"))
    credentials = client.OAuth2Credentials.from_json(session["credentials"])
    if credentials.access_token_expired:
        return redirect(url_for("oauth2callback"))
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build("calendar", "v3", http=http_auth)
    calendar = service.calendars().get(calendarId="primary").execute()
    return render_template("index.html", content=calendar["summary"])


# Begin oauth callback route
@app.route("/oauth2callback")
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        "../client_secrets.json",
        scope="https://www.googleapis.com/auth/calendar",
        redirect_uri=url_for("oauth2callback", _external=True),
    )
    if "code" not in request.args:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        auth_code = request.args.get("code")
        credentials = flow.step2_exchange(auth_code)
        session["credentials"] = credentials.to_json()
        return redirect(url_for("index"))


@app.route("/calendar")
def calendar():
    return render_template("calendar.html", content="virtual pet calendar")


@app.route("/inv")
def inventory():
    return render_template("inventory.html")


@app.route("/shop")
def shop():
    return render_template("shop.html")


if __name__ == "__main__":
    app.run()
