import os, flask, sys, httplib2, datetime, pyrebase
from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from firebase_admin import credentials, firestore, initialize_app, db
from oauth2client import client
from operator import itemgetter
from googleapiclient import discovery

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "password"

# Initialize Firestore DB
# default_app = initialize_app()
config = {
    "apiKey": "AIzaSyD-gV3V7Gn1KAPrZSI64H2fDVz2xR4NkuM",
    "authDomain": "virtual-pet-calendar.firebaseapp.com",
    "databaseURL": "https://virtual-pet-calendar-default-rtdb.firebaseio.com",
    "storageBucket": "virtual-pet-calendar.appspot.com",
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()
# db.child("users").child("Morty")
# data = {"name": "Mortimer 'Morty' Smith"}
# db.child("users").push(data)
auth = firebase.auth()

person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}

@app.route("/")
def index():
    if "person" not in session or not session["person"]["is_logged_in"]:
        return redirect(url_for("login"))
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
        scope=[
            "https://www.googleapis.com/auth/tasks",
            "https://www.googleapis.com/auth/calendar",
        ],
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
    if "person" not in session or not session["person"]["is_logged_in"]:
        return redirect(url_for("login"))
    if "credentials" not in session:
        return redirect(url_for("oauth2callback"))
    credentials = client.OAuth2Credentials.from_json(session["credentials"])
    if credentials.access_token_expired:
        return redirect(url_for("oauth2callback"))
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build("calendar", "v3", http=http_auth)

    now = datetime.datetime.utcnow().isoformat() + "Z"

    # Retrieve events
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            # timeMax=end_time,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])

    # Dict of dates to a list of events for that date
    dates = {}

    if not events:
        print("No events found")
    else:
        # print(f"Events for {target_date.date()}:")
        print("Events")
        for event in events:
            start_time = event["start"].get("dateTime", event["start"].get("date"))
            end_time = event["end"].get("dateTime", event["end"].get("date"))

            # Convert start_time and end_time to datetime objects
            start_datetime = datetime.datetime.fromisoformat(start_time)
            end_datetime = datetime.datetime.fromisoformat(end_time)

            # Format start_time and end_time in a standard format
            start_formatted = start_datetime.strftime("%H:%M")
            end_formatted = end_datetime.strftime("%H:%M")
            date = start_datetime.strftime("%D")

            # Add event info to proper date
            if not dates.get(date):
                dates[date] = []
            dates[date].append([event["summary"], start_formatted, end_formatted])

    # Tasks
    service = discovery.build("tasks", "v1", http=http_auth)
    results = service.tasklists().list().execute()

    prev_claim_str = db.child("users").child(session["person"]["uid"]).get().val()["prev_claim"]
    prev_claim_date = datetime.datetime.fromisoformat(prev_claim_str)
    tasksDates = {}
    tasklists = results.get("items", [])
    current_day = (datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)).isoformat() + "Z"
    display_min = (datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=10)).isoformat() + "Z"

    for item in tasklists:
        task_display = (
            service.tasks()
            .list(
                tasklist=item["id"],
                dueMin=display_min,
                dueMax=current_day,
                maxResults=10,
                showHidden=True,
            )
            .execute()
        )

        current_balance = db.child("users").child(session["person"]["uid"]).get().val()["balance"]
        # Always display at least some tasks
        displayed_tasks = task_display.get("items", [])
        for task in displayed_tasks:
            date = datetime.datetime.strptime(task["due"], "%Y-%m-%dT%H:%M:%S.%fZ")
            formattedDate = date.strftime("%D")

            if task["status"] == "completed":
                status = "Completed"
            else:
                status = "Incomplete"
            
            if not tasksDates.get(formattedDate):
                tasksDates[formattedDate] = []
            tasksDates[formattedDate].append([task["title"], status])

    return render_template("calendar.html",
                            dates=dates, 
                            tasksDates=dict(sorted(tasksDates.items(), reverse = True)), 
                            balance = current_balance,
                            prev_claim = prev_claim_date.strftime("%D"))

@app.route('/claim_tasks')
def claim_tasks():
    if "person" not in session or not session["person"]["is_logged_in"]:
        return redirect(url_for("login"))
    if "credentials" not in session:
        return redirect(url_for("oauth2callback"))
    credentials = client.OAuth2Credentials.from_json(session["credentials"])
    if credentials.access_token_expired:
        return redirect(url_for("oauth2callback"))
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build("tasks", "v1", http=http_auth)
    results = service.tasklists().list().execute()
    tasklists = results.get("items", [])

    current_day = (datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)).isoformat()
    prev_claim = db.child("users").child(session["person"]["uid"]).get().val()["prev_claim"]
    money_gained = 0
    current_balance = db.child("users").child(session["person"]["uid"]).get().val()["balance"]

    # Calculate money gained for task completions
    for item in tasklists:
        past_completed_tasks = (
            service.tasks()
            .list(
                tasklist=item["id"],
                dueMin=prev_claim + "Z",
                dueMax=current_day + "Z",
                showHidden=True,
            )
            .execute()
        )
        task_list = past_completed_tasks.get("items", [])
        for task in task_list:
            if task["status"] == "completed":
                completion_date = datetime.datetime.strptime(task["completed"], "%Y-%m-%dT%H:%M:%S.%fZ")
                due_date = datetime.datetime.strptime(task["due"], "%Y-%m-%dT%H:%M:%S.%fZ")
                if (completion_date - due_date).days < 1:
                    money_gained += 100
    # Update values for current user
    db.child("users").child(session["person"]["uid"]).update({"balance": current_balance + money_gained})
    db.child("users").child(session["person"]["uid"]).update({"prev_claim": current_day})
    return ('', 204)


@app.route("/inv")
def inventory():
    if "person" not in session or not session["person"]["is_logged_in"]:
        return redirect(url_for("login"))
    current_balance = db.child("users").child(session["person"]["uid"]).get().val()["balance"]
    return render_template("inventory.html", balance = current_balance)


@app.route("/shop")
def shop():
    if "person" not in session or not session["person"]["is_logged_in"]:
        return redirect(url_for("login"))
    current_balance = db.child("users").child(session["person"]["uid"]).get().val()["balance"]
    itemData = db.child("items").get().val()
    itemCount = db.child("users").child(session["person"]["uid"]).child("items").get().val()
    # User has no items
    if (not itemCount):
        itemCount = {}
    
    items = []
    for id, item in itemData.items():
        item["id"] = id
        item["count"] = itemCount.get(id, 0)
        items.append(item)
    
    # Test items
    for i in range(3):
        items.append({"name": "Test Item " + str(i), "image": "https://bulma.io/images/placeholders/640x320.png",
                      "description": "Description " + str(i), "price": 50*i})
    
    items.sort(key=itemgetter("price"))
    return render_template("shop.html", itemCount=itemCount, balance = current_balance, items=items, zip=zip)

# Redirected here when a buy button is clicked
@app.route("/buy", methods=["POST"])
def buy():
    if "person" not in session or not session["person"]["is_logged_in"]:
        return redirect(url_for("login"))
    spent = int(request.form["price"])
    id = request.form["id"]
    current_balance = db.child("users").child(session["person"]["uid"]).get().val()["balance"]
    itemCount = db.child("users").child(session["person"]["uid"]).child("items").get().val()
    # User has no items
    if (not itemCount):
        itemCount = {}
    # Update balance and item count
    if current_balance >= spent:
        db.child("users").child(session["person"]["uid"]).update({"balance": current_balance - spent})
        db.child("users").child(session["person"]["uid"]).child("items").update({id: itemCount.get(id, 0) + 1})
    return redirect(url_for("shop"))


@app.route("/login")
def login():
    return render_template("login.html")


# If someone clicks on login, they are redirected to /result
@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":  # Only if data has been posted
        result = request.form  # Get the data
        email = result["email"]
        password = result["password"]
        try:
            # Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            # Insert the user data in the session object
            session["person"] = {
                "is_logged_in": True,
                "email": user["email"],
                "uid": user["localId"],
                # Get the name of the user
                "name": db.child("users").child(user["localId"]).get().val()["name"],
                "prev_claim": db.child("users").child(user["localId"]).get().val()["prev_claim"],
                "balance": db.child("users").child(user["localId"]).get().val()["balance"],
            }

            # Redirect to welcome page
            return redirect(url_for("index"))
        except:
            # If there is any error, redirect back to login
            return redirect(url_for("login"))
    else:
        if session.get("person") and session["person"]["is_logged_in"]:
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":  # Only listen to POST
        result = request.form  # Get the data submitted
        email = result["email"]
        password = result["password"]
        name = result["name"]
        try:
            # Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            # Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            current_day = (datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)).isoformat()
            session["person"] = {
                "is_logged_in": True,
                "email": user["email"],
                "uid": user["localId"],
                # Get the name of the user
                "name": name,
                "prev_claim": current_day,
                "balance": 0,
            }
            # Append data to the firebase realtime database
            data = {"name": name, 
                    "email": email, 
                    "prev_claim": session["person"]["prev_claim"], 
                    "balance": session["person"]["balance"]}
            
            db.child("users").child(session["person"]["uid"]).set(data)
            # Go to welcome page
            return redirect(url_for("index"))
        except:
            # If there is any error, redirect to register
            return redirect(url_for("register"))

    else:
        if session.get("person") and session["person"]["is_logged_in"]:
            return redirect(url_for("index"))
        else:
            return redirect(url_for("signup"))


if __name__ == "__main__":
    app.run()
