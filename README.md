# AI/ML-Enhanced Multi-Factor Authentication System

iA secure Flask-based authentication system developed to mitigate password guessing attacks using multi-factor authentication (MFA), suspicious login detection, and rule-based risk scoring.

## Features

- Username and password authentication
- OTP-based multi-factor authentication (MFA)
- Rule-based suspicious login detection
- Unknown device detection
- Temporary account blocking
- Login delay for medium-risk attempts
- Password hashing
- Countdown timer for blocked users
- Responsive modern UI

## Technologies Used

- Python
- Flask
- HTML/CSS
- JSON Database
- Werkzeug Security

## System Flow

1. User enters username, password, and device ID
2. System verifies credentials
3. Risk engine evaluates login behavior
4. Risk level is calculated
5. System applies mitigation response:
   - Low Risk → OTP verification
   - Medium Risk → Delay + OTP
   - High Risk → Temporary block
6. OTP verification is performed
7. Access granted or denied

## Project Structure

```bash
project/
│
├── app.py
├── users.json
├── otp_store.json
├── templates/
│   ├── login.html
│   ├── otp.html
│   ├── blocked.html
│   └── success.html
└── static/
    └── style.css
```

## Installation

Clone the repository:

```bash
git clone <repository-link>
```

Install required libraries:

```bash
pip install flask werkzeug
```

Run the application:

```bash
python app.py
```

Open browser:

```text
http://127.0.0.1:5000
```

## Screenshots

(Add screenshots here later)

## Team Members

- Your Name
- Team Member 2
- Team Member 3

## Disclaimer

This project was developed for educational purposes as part of a Computer Security course project.