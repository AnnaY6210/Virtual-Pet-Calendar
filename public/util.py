import os, flask, sys, httplib2, datetime, pyrebase
from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from oauth2client import client

    
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
    formatted_tasks = {}
    for task_list in tasklists:
        # Add the claimable currency of the tasklist to the total
        # Tasks have their reward defined by the positive integer after their title after a bar ("|")
        currency_per_task = 10
        suffix = task_list["title"].split("|")[-1].strip()
        if suffix.isdigit():
            currency_per_task = int(suffix)
        claimable_money += calculate_money(service, task_list, currency_per_task, prev_claim_str)

        # Generate list of tasks for display
        tasks_to_display = (
            service.tasks()
            .list(
                tasklist=task_list["id"],
                dueMax=current_day.isoformat() + "Z",
                maxResults=40,
                showHidden=True,
            )
            .execute()
        )
        # Generate formatted dates and task statuses
        tasks = tasks_to_display.get("items", [])
        for task in tasks:
            date = datetime.datetime.strptime(task["due"], "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_date = date.strftime("%D")

            if task["status"] == "completed":
                completion_date = datetime.datetime.strptime(task["completed"], "%Y-%m-%dT%H:%M:%S.%fZ")
                due_date = datetime.datetime.strptime(task["due"], "%Y-%m-%dT%H:%M:%S.%fZ")
                # Status for on-time completion
                if (completion_date - due_date).days < 1:
                    status = "Completed [+" + str(currency_per_task) + "]"
                # Status for late completion
                else:
                    status = "Completed Late [<s>" + str(currency_per_task) + "</s>]"
            else:
                status = "Incomplete"
            
            if not formatted_tasks.get(formatted_date):
                formatted_tasks[formatted_date] = []
            formatted_tasks[formatted_date].append([task["title"], status])
    return formatted_tasks, claimable_money

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

def get_shop_items(db):
    return db.child("items").get().val()

def get_user_items(db, user_id):
    item_count = db.child("users").child(user_id).child("items").get().val()
    if (not item_count):
        item_count = {}
    return item_count

def get_pet_info(db):
    return db.child("pets").get().val()

def get_user_pets_list(db, user_id):
    user_pets = db.child("users").child(user_id).child("pets").get().val()
    if (not user_pets):
        user_pets = {}
    pet_info = get_pet_info(db)
    pets = []
    for id, item in user_pets.items():
        time_now = datetime.datetime.now()
        time_now_string = time_now.strftime("%m/%d/%Y, %H:%M:%S.%f")
        if "last_time" not in item.keys():
            db.child("users").child(user_id).child("pets").child(id).update({"last_time": time_now_string})
            time_then = time_now
        else:
            time_then = datetime.datetime.strptime(item["last_time"], "%m/%d/%Y, %H:%M:%S.%f")
        delta = time_now - time_then

        pet = {}
        pet["id"] = id
        pet["equip"] = item["equip"]
        pet["image"] = pet_info[id]["image"]
        if item["equip"] is True:
            if item["health"] > 0:
                pet["health"] = item["health"] - (delta.days * 10)
                db.child("users").child(user_id).child("pets").child(id).update({"health": pet["health"], 
                                                                                 "last_time": time_now_string})
            else:
                pet["health"] = item["health"]
        else:
            pet["health"] = item["health"]
            new_time = (time_then + delta).strftime("%m/%d/%Y, %H:%M:%S.%f")
            db.child("users").child(user_id).child("pets").child(id).update({"last_time": new_time})
        pets.append(pet)
    return pets
