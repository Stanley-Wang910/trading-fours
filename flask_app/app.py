from flask import Flask, request, redirect, session, jsonify
import os
import requests
import base64
from urllib.parse import urlencode
import string
import random
from dotenv import load_dotenv
import spotipy 
from spotipy import Spotify

# Load environment variables
load_dotenv()


app = Flask(__name__)

# Set a secret key for session management
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Generate a random state string
def generate_random_string(length=16):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

@app.route('/auth/login')
def auth_login():
    scope = "streaming user-read-email user-read-private"
    state = generate_random_string()
    params = {
        'response_type': 'code',
        'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
        'scope': scope,
        'redirect_uri': 'http://localhost:3000/auth/callback',
        'state': state
    }
    url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return redirect(url)

@app.route('/auth/callback')
def auth_callback():
    code = request.args.get('code')
    # Exchange code for token
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    # Authorization header
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

    auth_header = {
        'Authorization': f"Basic {client_creds_b64}",
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    auth_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000/auth/callback',
    }
    response = requests.post('https://accounts.spotify.com/api/token', data=auth_data, headers=auth_header)
    if response.status_code == 200:
        token_info = response.json()
        session['access_token'] = token_info.get('access_token')
        # Redirecting or handling logic here
        return redirect('/')
    else:
        return "Error in token exchange", response.status_code

@app.route('/auth/token')
def get_token():
    access_token = session.get('access_token')
    if access_token:
        return jsonify({'access_token': access_token})

@app.route('/clear_session')
def clear_session():
    session.clear()
    return "Session data cleared"

@app.route('/user/data')
def get_user_data():
    access_token = session.get('access_token')
    if access_token:
        # headers = {
        #     'Authorization': f"Bearer {access_token}"
        # }
        # response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        # if response.status_code == 200:
        #     user_data = response.json()
        #     # Process and return user data here
        sp = Spotify(auth=access_token)
        user_data = sp.current_user()
        return jsonify(user_data)
    else:
            return jsonify({"error": "Access token not found"}), 401


    

if __name__ == '__main__':
    app.run(debug=True)
