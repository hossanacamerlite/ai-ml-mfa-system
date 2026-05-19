from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import random
import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "sample_secret_key_for_demo_only"

USERS_FILE = "users.json"
OTP_FILE = "otp_store.json"

# Track user attempts
login_tracker = {}

BLOCK_THRESHOLD = 5
BLOCK_DURATION = 60  # seconds


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def load_otp_store():
    if os.path.exists(OTP_FILE):
        with open(OTP_FILE, "r") as f:
            return json.load(f)
    return {}


def save_otp_store(data):
    with open(OTP_FILE, "w") as f:
        json.dump(data, f, indent=4)


def generate_otp():
    return str(random.randint(100000, 999999))


def get_current_hour():
    return datetime.now().hour


def is_unusual_hour():
    return 1 if get_current_hour() < 5 else 0


def initialize_user_tracker(username):
    if username not in login_tracker:
        login_tracker[username] = {
            "failed_attempts": 0,
            "last_attempt_time": 0,
            "blocked_until": 0
        }


def extract_features(username, device_id, password_correct):
    initialize_user_tracker(username)

    tracker = login_tracker[username]
    current_time = time.time()

    short_interval = 1 if current_time - tracker["last_attempt_time"] < 5 else 0
    unusual_hour = is_unusual_hour()

    users = load_users()
    unknown_device = 1

    if username in users:
        if device_id == users[username]["known_device"]:
            unknown_device = 0

    features = {
        "failed_attempts": tracker["failed_attempts"],
        "short_interval": short_interval,
        "unknown_device": unknown_device,
        "unusual_hour": unusual_hour,
        "password_match": 1 if password_correct else 0
    }

    tracker["last_attempt_time"] = current_time
    return features


def simple_risk_engine(features):
    score = 0

    if features["failed_attempts"] >= 3:
        score += 2
    if features["short_interval"] == 1:
        score += 2
    if features["unknown_device"] == 1:
        score += 1
    if features["unusual_hour"] == 1:
        score += 1
    if features["password_match"] == 0:
        score += 2

    if score >= 5:
        return "high", score
    elif score >= 3:
        return "medium", score
    else:
        return "low", score


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        device_id = request.form["device_id"]

        users = load_users()
        initialize_user_tracker(username)
        tracker = login_tracker[username]

        # Check if blocked
        if time.time() < tracker["blocked_until"]:
            remaining = int(tracker["blocked_until"] - time.time())
            return render_template("blocked.html", remaining=remaining)

        password_correct = False
        if username in users and check_password_hash(users[username]["password"], password):
            password_correct = True

        features = extract_features(username, device_id, password_correct)
        risk_level, risk_score = simple_risk_engine(features)

        if not password_correct:
            tracker["failed_attempts"] += 1

            if tracker["failed_attempts"] >= BLOCK_THRESHOLD:
                tracker["blocked_until"] = time.time() + BLOCK_DURATION
                return render_template("blocked.html", remaining=BLOCK_DURATION)

            return render_template(
                "login.html",
                error=f"Invalid password. Risk: {risk_level}, Score: {risk_score}"
            )

        tracker["failed_attempts"] = 0

        if risk_level == "high":
            tracker["blocked_until"] = time.time() + BLOCK_DURATION
            return render_template("blocked.html", remaining=BLOCK_DURATION)

        elif risk_level == "medium":
            time.sleep(3)

        # Generate OTP
        otp = generate_otp()
        otp_store = load_otp_store()
        otp_store[username] = otp
        save_otp_store(otp_store)

        session["username"] = username
        session["risk_level"] = risk_level

        print(f"[OTP for {username}]: {otp}")

        return redirect(url_for("otp_verification"))

    return render_template("login.html")


@app.route("/otp", methods=["GET", "POST"])
def otp_verification():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    risk_level = session.get("risk_level", "low")

    if request.method == "POST":
        entered_otp = request.form["otp"]

        otp_store = load_otp_store()
        correct_otp = otp_store.get(username)

        if entered_otp == correct_otp:
            otp_store.pop(username, None)
            save_otp_store(otp_store)

            return render_template("success.html", username=username, risk_level=risk_level)

        return render_template("otp.html", error="Invalid OTP", risk_level=risk_level)

    return render_template("otp.html", risk_level=risk_level)


@app.route("/success")
def success():
    return render_template("success.html")


if __name__ == "__main__":
    app.run(debug=True)