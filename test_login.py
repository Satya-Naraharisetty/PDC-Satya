from flask import Flask, redirect, url_for, session, request, jsonify
import os
from dotenv import load_dotenv
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# Allow HTTP for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
REDIRECT_URI = "http://localhost:5000/callback/google"

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/")
def index():
    return """
        <button onclick="window.location.href='/login/google'">
            Login with Google
        </button>
    """

@app.route("/login/google")
def login():
    google_cfg = get_google_provider_cfg()
    authorization_endpoint = google_cfg["authorization_endpoint"]
    
    request_uri = (
        f"{authorization_endpoint}?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=openid%20email%20profile"
    )
    return redirect(request_uri)

@app.route("/callback/google")
def callback():
    code = request.args.get("code")
    if not code:
        return "No code provided", 400

    google_cfg = get_google_provider_cfg()
    token_endpoint = google_cfg["token_endpoint"]

    # Exchange authorization code for tokens
    token_response = requests.post(
        token_endpoint,
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
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
            session['user'] = {
                "email": id_info.get("email"),
                "name": id_info.get("name"),
                "picture": id_info.get("picture"),
            }
            return jsonify(session['user'])
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return jsonify({"error": "Failed to obtain ID token"}), 400

if __name__ == "__main__":
    app.run(port=5000, debug=True)
