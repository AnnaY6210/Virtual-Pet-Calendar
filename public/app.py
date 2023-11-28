import os, flask, sys, httplib2, datetime, pyrebase
import util
from flask import Flask, request, jsonify, redirect, url_for, render_template, session
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

    return redirect(url_for("calendar"))

    
TASK_SCOPE = "https://www.googleapis.com/auth/tasks"
CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar"   

# Begin oauth callback route
@app.route("/oauth2callback")
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        "../client_secrets.json",
        scope=[TASK_SCOPE,CALENDAR_SCOPE],
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
    # gets user pet for this page
    pets = util.get_user_pets_list(db, session["person"]["uid"], session["person"]["token"])

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
        dates = util.format_events(events)

    # Task variables
    service = discovery.build("tasks", "v1", http=http_auth)
    results = service.tasklists().list().execute()
    tasklists = results.get("items", [])
    prev_claim_str = util.get_prev_claim(db, session["person"]["uid"])
    prev_claim_date = datetime.datetime.fromisoformat(prev_claim_str)
    claimable_money = 0
    current_balance = util.get_balance(db, session["person"]["uid"])

    # Parse tasks in each of the user's tasklists
    tasks_dates, claimable_money = util.format_tasks(tasklists, service, prev_claim_str)
        
    return render_template("calendar.html",
                            dates=dates, 
                            tasks_dates=dict(sorted(tasks_dates.items(), reverse = True)), 
                            balance = current_balance,
                            prev_claim = prev_claim_date.strftime("%D"),
                            claimable_money = claimable_money,
                            pets=pets,
                            person=session["person"],)
      

@app.route("/claim_tasks")
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
    current_day = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    money_gained = 0
    current_balance = util.get_balance(db, session["person"]["uid"])
    prev_claim = util.get_prev_claim(db, session["person"]["uid"])

    # Calculate money gained for task completions
    for task_list in tasklists:
        currency_per_task = util.DEFAULT_REWARD
        if task_list["title"].split()[-1].isdigit():
            currency_per_task = int(task_list["title"].split()[-1])
        money_gained += util.calculate_money(service, task_list, currency_per_task, prev_claim)
        
    # Update values for current user
    if money_gained > 0:
        db.child("users").child(session["person"]["uid"]).update({"balance": current_balance + money_gained}, session["person"]["token"])
        db.child("users").child(session["person"]["uid"]).update({"prev_claim": (current_day + datetime.timedelta(days=1)).isoformat()}, session["person"]["token"])
    return jsonify(balance=current_balance + money_gained,
                   prev_claim=current_day.strftime("%D"))



@app.route("/inv")
def inventory():
    if "person" not in session or not session["person"]["is_logged_in"]:
        return redirect(url_for("login"))
    if "credentials" not in session:
        return redirect(url_for("oauth2callback"))
    credentials = client.OAuth2Credentials.from_json(session["credentials"])
    if credentials.access_token_expired:
        return redirect(url_for("oauth2callback"))
    
    # gets users pet
    pets = util.get_user_pets_list(db, session["person"]["uid"], session["person"]["token"])
    current_balance = util.get_balance(db, session["person"]["uid"])
    item_data = util.get_shop_items(db)
    item_count = util.get_user_items(db,session["person"]["uid"])
    items = []
    for id, item in item_data.items():
        if (id in item_count.keys()):
            item["id"] = id
            item["count"] = item_count[id]
            items.append(item)
    items.sort(key=itemgetter("count"), reverse=True)
    return render_template(
        "inventory.html", pets=pets, item_count=item_count, balance=current_balance,
        items=items, zip=zip, person=session["person"]
    )


@app.route("/shop")
def shop():
    if "person" not in session or not session["person"]["is_logged_in"]:
        return redirect(url_for("login"))
    if "credentials" not in session:
        return redirect(url_for("oauth2callback"))
    credentials = client.OAuth2Credentials.from_json(session["credentials"])
    if credentials.access_token_expired:
        return redirect(url_for("oauth2callback"))
    
    current_balance = util.get_balance(db, session["person"]["uid"])
    item_data = util.get_shop_items(db)
    item_count = util.get_user_items(db,session["person"]["uid"])
    items = []
    pets = util.get_user_pets_list(db, session["person"]["uid"], session["person"]["token"])
    for id, item in item_data.items():
        item["id"] = id
        item["count"] = item_count.get(id, 0)
        items.append(item)
    items.sort(key=itemgetter("price"))
    return render_template("shop.html", pets=pets, balance = current_balance, items=items, zip=zip, person=session["person"],)



# Redirected here when a buy button is clicked
@app.route("/buy", methods=["POST"])
def buy():
    if "person" not in session or not session["person"]["is_logged_in"]:
        return redirect(url_for("login"))
    if "credentials" not in session:
        return redirect(url_for("oauth2callback"))
    credentials = client.OAuth2Credentials.from_json(session["credentials"])
    if credentials.access_token_expired:
        return redirect(url_for("oauth2callback"))
    
    spent = int(request.form["price"])
    id = request.form["id"]
    print(db.child("users").child(session["person"]["uid"]).get().val())
    current_balance = db.child("users").child(session["person"]["uid"]).get().val()["balance"]
    item_count = util.get_user_items(db,session["person"]["uid"])
    pet_info = util.get_pet_info(db)
    # Update balance and item count
    if current_balance >= spent:
        db.child("users").child(session["person"]["uid"]).update({"balance": current_balance - spent}, session["person"]["token"], session["person"]["token"])
        if id in pet_info.keys():
            db.child("users").child(session["person"]["uid"]).child("pets").child(id).update({
                "health": 100,
                "equip": False,
                "last_time": datetime.datetime.now()
            }, session["person"]["token"])
        db.child("users").child(session["person"]["uid"]).child("items").update({id: item_count.get(id, 0) + 1}, session["person"]["token"])
    return redirect(url_for("shop"))


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/logout")
def logout():
    if session:
        session.clear()
    return redirect(url_for("login"))


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
                "token": user["idToken"],
                "uid": user["localId"],
                # Get the name of the user
                "name": db.child("users").child(user["localId"]).get().val()["name"],
                "prev_claim": util.get_prev_claim(db, user["localId"]),
                "balance": db.child("users")
                .child(user["localId"])
                .get()
                .val()["balance"],
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
            current_day = (
                datetime.datetime.utcnow().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            ).isoformat()
            session["person"] = {
                "is_logged_in": True,
                "email": user["email"],
                "uid": user["localId"],
                "token": user["idToken"],
                # Get the name of the user
                "name": name,
                "prev_claim": current_day,
                "balance": 0,
            }
            # Append data to the firebase realtime database
            data = {
                "name": name,
                "email": email,
                "prev_claim": session["person"]["prev_claim"],
                "balance": session["person"]["balance"],
            }

            db.child("users").child(session["person"]["uid"]).set(data, session["person"]["token"])
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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
