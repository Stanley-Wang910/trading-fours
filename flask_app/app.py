from flask import Flask, request, jsonify, session, redirect, render_template
from dotenv import load_dotenv
import os
import requests
import urllib.parse
import random
import string
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = 'penis'
#auth = SpotifyClient(app)
load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

RECENTLY_PLAYED_URL = 'https://api.spotify.com/v1/me/player/recently-played'
@app.route('/')
def index():
    return redirect('/login')

@app.route('/login')
def login():
    auth_manager = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope='user-read-private user-read-email user-read-recently-played user-top-read')
    url = auth_manager.get_authorize_url()
    return redirect(url)



@app.route('/callback')
def callback():
    code = request.args.get('code')
    auth_manager = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope='user-read-private user-read-email user-read-recently-played user-top-read')
    token_info = auth_manager.get_access_token(code)
    session['access_token'] = token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
    return redirect('/homepage')

@app.route('/homepage')
def display_homepage():

    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    auth_manager = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope='user-read-private user-read-email user-read-recently-played user-top-read')
    auth_manager.get_cached_token()  # This will automatically refresh the token if it's expired
    token_info = auth_manager.get_cached_token()
    session['access_token'] = token_info['access_token']
    session['expires_at'] = token_info['expires_in'] + datetime.now().timestamp()

    sp = spotipy.Spotify(auth_manager=auth_manager)
    # Get the selected time range from the query parameters
    time_range = request.args.get('time_range', 'short_term')

    # Fetch user profile information
    user_profile = sp.me()
    user_name_data = user_profile.get('display_name', 'User')

    
    # Fetch top artists
    top_artists_data = sp.current_user_top_artists(limit=10, time_range=time_range)

    # Fetch recently played tracks
    recently_played = sp.current_user_recently_played(limit=5)

    return render_template('index.html', user_name=user_name_data, top_artists = top_artists_data, recently_played_data=recently_played)



    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)