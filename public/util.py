import os, flask, sys, httplib2, datetime, pyrebase
from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from oauth2client import client
def login_check(session):
    if "person" not in session or not session["person"]["is_logged_in"]:
        return redirect(url_for("login"))
    if "credentials" not in session:
        return redirect(url_for("oauth2callback"))
    credentials = client.OAuth2Credentials.from_json(session["credentials"])
    if credentials.access_token_expired:
        return redirect(url_for("oauth2callback"))
    return credentials
    
def format_events(events):
    dates = {}
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
    return dates

def format_tasks(tasklists, service, prev_claim_str):
    claimable_money = 0
    current_day = (datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
    tasks_dates = {}
    for task_list in tasklists:
        # Add the claimable currency of the tasklist to the total
        # Tasks have their reward defined by the positive integer after their title after a bar ("|")
        currency_per_task = 10
        suffix = task_list["title"].split("|")[-1].strip()
        if suffix.isdigit():
            currency_per_task = int(suffix)
        claimable_money += calculate_money(service, task_list, currency_per_task, prev_claim_str)

        # List of tasks for display
        task_display = (
            service.tasks()
            .list(
                tasklist=task_list["id"],
                dueMax=current_day.isoformat() + "Z",
                maxResults=40,
                showHidden=True,
            )
            .execute()
        )
        # Always display at least some tasks
        tasks = task_display.get("items", [])
        for task in tasks:
            date = datetime.datetime.strptime(task["due"], "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_date = date.strftime("%D")

            if task["status"] == "completed":
                completion_date = datetime.datetime.strptime(task["completed"], "%Y-%m-%dT%H:%M:%S.%fZ")
                due_date = datetime.datetime.strptime(task["due"], "%Y-%m-%dT%H:%M:%S.%fZ")
                if (completion_date - due_date).days < 1:
                    status = "Completed [+" + str(currency_per_task) + "]"
                else:
                    status = "Completed Late [<s>" + str(currency_per_task) + "</s>]"
            else:
                status = "Incomplete"
            
            if not tasks_dates.get(formatted_date):
                tasks_dates[formatted_date] = []
            tasks_dates[formatted_date].append([task["title"], status])
    return tasks_dates, claimable_money

# Function for calculating the currency reward for a given tasklist
def calculate_money(service, tasklist, currency_per_task, prev_claim):
    current_day = (datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)).isoformat()
    total = 0
    past_completed_tasks = (
            service.tasks()
            .list(
                tasklist=tasklist["id"],
                dueMin=prev_claim + "Z",
                dueMax=current_day + "Z",
                showHidden=True,
            )
            .execute()
        )
    tasks = past_completed_tasks.get("items", [])
    for task in tasks:
        if task["status"] == "completed":
            completion_date = datetime.datetime.strptime(task["completed"], "%Y-%m-%dT%H:%M:%S.%fZ")
            due_date = datetime.datetime.strptime(task["due"], "%Y-%m-%dT%H:%M:%S.%fZ")
            if (completion_date - due_date).days < 1:
                total += currency_per_task
    return total

def get_prev_claim(db, user_id):
    return db.child("users").child(user_id).get().val()["prev_claim"]

def get_balance(db, user_id):
    return db.child("users").child(user_id).get().val()["balance"]

def get_user(db, user_id):
    return db.child("users").child(user_id)

def get_shop_items(db):
    return db.child("items").get().val()

def get_user_items(db, user_id):
    item_count = db.child("users").child(user_id).child("items").get().val()
    if (not item_count):
        item_count = {}
    return item_count
