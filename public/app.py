import os, flask, sys, httplib2, datetime
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
    return render_template("index.html", content="add cute pet here")


# Begin oauth callback route
@app.route("/oauth2callback")
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        "../client_secrets.json",
        scope=["https://www.googleapis.com/auth/tasks", "https://www.googleapis.com/auth/calendar"],
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
    if "credentials" not in session:
        return redirect(url_for("oauth2callback"))
    credentials = client.OAuth2Credentials.from_json(session["credentials"])
    if credentials.access_token_expired:
        return redirect(url_for("oauth2callback"))
    http_auth = credentials.authorize(httplib2.Http())

    # get all events from calendar
    target_date = datetime.datetime.now()  # Change to your desired date

    # Define the start and end times for the target day
    start_time = target_date.replace(hour=0, minute=0, second=0).isoformat() + "Z"
    end_time = target_date.replace(hour=23, minute=59, second=59).isoformat() + "Z"

    # Retrieve events for the target day
    eventservice = discovery.build("calendar", "v3", http=http_auth)
    
    events_result = eventservice.events().list(
            calendarId="primary",
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

    events = events_result.get("items", [])
    eventList = []
    if not events:
        print("No events found for the specified date.")
    else:
        print(f"Events for {target_date.date()}:")
        for event in events:
            start_time = event["start"].get("dateTime", event["start"].get("date"))
            end_time = event["end"].get("dateTime", event["end"].get("date"))

            # Convert start_time and end_time to datetime objects
            start_datetime = datetime.datetime.fromisoformat(start_time)
            end_datetime = datetime.datetime.fromisoformat(end_time)

            # Format start_time and end_time in a standard format
            start_formatted = start_datetime.strftime("%H:%M")
            end_formatted = end_datetime.strftime("%H:%M")
            eventList.append(f'{start_formatted} - {end_formatted}: {event["summary"]}')

    
    today = datetime.datetime.now()
    prev_login = datetime.datetime(2023, 10, 27) # TEMPORARY LINE

    taskservice = discovery.build("tasks", "v1", http=http_auth)
    results = taskservice.tasklists().list().execute()
    tasklists = results.get("items", [])
    displayTasks = []
    for item in tasklists:
        pastTasks = taskservice.tasks().list(tasklist = item['id'], dueMin = prev_login.isoformat() + "Z", dueMax = today.isoformat() + "Z").execute()
        todayTasks = taskservice.tasks().list(tasklist = item['id'], dueMin = today.isoformat() + "Z", dueMax = (today + datetime.timedelta(days=1)).isoformat() + "Z").execute()
        
        tlist = pastTasks.get("items", [])
        for task in tlist:
            displayTasks.append((task['title'], task['due'], task['status']))
            
        tlist = todayTasks.get("items", [])
        for task in tlist:
            displayTasks.append((task['title'], task['due'], task['status']))

    return render_template("calendar.html", content=displayTasks)


@app.route("/inv")
def inventory():
    return render_template("inventory.html")


@app.route("/shop")
def shop():
    return render_template("shop.html")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
