import os
from datetime import datetime
from flask import Flask, redirect, url_for, session, render_template, request, flash
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import pytz

# Load .env if present
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# OAuth Configuration (Google)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("Warning: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set. Create credentials and set them as env vars.")

oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    access_token_url="https://oauth2.googleapis.com/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v3/",
    client_kwargs={"scope": "openid email profile"},
)

def get_indian_time():
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(tz).strftime("%d-%m-%Y %H:%M:%S")

@app.route("/")
def index():
    user = session.get("user")
    return render_template("index.html", user=user, indian_time=get_indian_time())

@app.route("/login")
def login():
    redirect_uri = url_for("authorize", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route("/authorize")
def authorize():
    token = oauth.google.authorize_access_token()
    if token is None:
        flash("Authorization failed.")
        return redirect(url_for("index"))
    
    userinfo = oauth.google.parse_id_token(token)
    if not userinfo:
        userinfo = oauth.google.get("userinfo").json()

    session["user"] = {
        "name": userinfo.get("name"),
        "email": userinfo.get("email"),
        "picture": userinfo.get("picture"),
    }
    return redirect(url_for("profile"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been signed out.")
    return redirect(url_for("index"))

# run app
if __name__ == "__main__":
    app.run(debug=True, port=5000)