import os
from datetime import datetime
from flask import Flask, redirect, url_for, session, render_template, request, flash
from dotenv import load_dotenv
import pytz
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Load .env if present
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# OAuth Configuration (Google)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")
REDIRECT_URL = "http://localhost:5000/callback/google"

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("Warning: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set. Create credentials and set them as env vars.")


def get_indian_time():
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(tz).strftime("%d-%m-%Y %H:%M:%S")

@app.route("/")
def index():
    user = session.get("user")
    return render_template("index.html", user=user, indian_time=get_indian_time())

@app.route("/login/google")
def login():
    google_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_cfg["authorization_endpoint"]
    
    request_uri = (
        f"{authorization_endpoint}?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URL}"
        f"&scope=openid%20email%20profile"
    )
    return redirect(request_uri)

@app.route("/callback/google")
def callback():
    code = request.args.get("code")
    if not code:
        return "No code provided", 400

    google_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_cfg["token_endpoint"]

    # Exchange authorization code for tokens
    token_response = requests.post(
        token_endpoint,
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": REDIRECT_URL,
            "grant_type": "authorization_code",
        },
    )
    token_response_data = token_response.json()
    id_token_str = token_response_data.get("id_token")

    if id_token_str:
        try:
            # Verify the token and get user info
            id_info = id_token.verify_oauth2_token(
                id_token_str, google_requests.Request(), GOOGLE_CLIENT_ID
            )
            # Store user info in session
            session['user'] = {
                "email": id_info.get("email"),
                "name": id_info.get("name"),
                "picture": id_info.get("picture"),
            }
            # Redirect to /profile instead of returning JSON
            return redirect(url_for("profile"))
        except Exception as e:
            return f"Error verifying token: {e}", 400

    return "Failed to obtain ID token", 400

@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = session.get("user")
    if not user:
        return redirect(url_for("index"))

    pattern_output = None
    if request.method == "POST":
        try:
            n = int(request.form.get("lines", "0"))
        except ValueError:
            flash("Please enter a valid integer.")
            return redirect(url_for("profile"))

        if n <= 0 or n > 100:
            flash("Please enter a number between 1 and 100.")
            return redirect(url_for("profile"))

        pattern_output = generate_design(n)

    return render_template("profile.html", user=user, indian_time=get_indian_time(), pattern_output=pattern_output)

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been signed out.")
    return redirect(url_for("index"))

def generate_design(num_lines: int) -> str:
    """Generate diamond pattern with 'FORMULAQSOLUTIONS'."""
    # Validate
    if not 1 <= num_lines <= 100:
        return "Error: Input must be between 1 and 100."

    if num_lines % 2 == 0:
        print(f"Input is an even number ({num_lines}). Creating a pattern for the next odd number: {num_lines + 1}.")
        num_lines += 1

    source_text = "FORMULAQSOLUTIONS"
    n_text = len(source_text)
    mid_point = num_lines // 2

    lines = []

    # Upper half
    for i in range(mid_point + 1):
        length = 2 * i + 1
        num_spaces = (num_lines - length) // 2
        start_index = i % n_text
        substring = "".join(source_text[(start_index + j) % n_text] for j in range(length))
        lines.append(" " * num_spaces + substring)

    # Lower half
    for i in range(1, mid_point + 1):
        length = num_lines - 2 * i
        num_spaces = (num_lines - length) // 2
        start_index = (mid_point + i) % n_text
        substring = "".join(source_text[(start_index + j) % n_text] for j in range(length))
        lines.append(" " * num_spaces + substring)

    return "\n".join(lines)
    

# run app
if __name__ == "__main__":
    app.run(debug=True, port=5000)