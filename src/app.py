from flask import Flask, request, jsonify, session, redirect, render_template
from dotenv import load_dotenv
import os
import requests
import urllib.parse
import random
import string
from datetime import datetime

from spotify_client import SpotifyClient

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
    scope = 'user-read-private user-read-email user-read-recently-played user-top-read'

    params = {
        'client_id':CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        # Only for testing, remove this later
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return render_template('login.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

        return redirect('/homepage')

@app.route('/homepage')
def display_homepage():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    # Get the selected time range from the query parameters
    time_range = request.args.get('time_range', 'short_term')

    # Fetch user profile information
    response_user_profile = requests.get(API_BASE_URL + 'me', headers=headers)
    user_profile = response_user_profile.json()
    user_name_data = user_profile.get('display_name', 'User')

    # Fetch top artists
    response_top_artists = requests.get(API_BASE_URL + f'me/top/artists?time_range={time_range}&limit=10', headers=headers)
    top_artists_data = response_top_artists.json()   

    # Fetch recently played tracks
    response_recently_played = requests.get(API_BASE_URL + 'me/player/recently-played?limit=5', headers=headers)
    recently_played = response_recently_played.json() 

    return render_template('index.html', user_name=user_name_data, top_artists = top_artists_data, recently_played_data=recently_played)


@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    # Fetch user playlists
    response_playlists = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    playlists = response_playlists.json()

    # Fetch recently played tracks
    response_recently_played = requests.get(API_BASE_URL + 'me/player/recently-played', headers=headers)
    recently_played = response_recently_played.json()

    # Fetch top artists
    response_top_artists = requests.get(API_BASE_URL + 'me/top/artists', headers=headers)
    top_artists = response_top_artists.json()

    # Fetch user profile information
    response_user_profile = requests.get(API_BASE_URL + 'me', headers=headers)
    user_profile = response_user_profile.json()
    user_name_data = user_profile.get('display_name', 'User')

    #return jsonify(top_artists)

    return render_template('playlists.html', playlist=playlists, recently_played_data=recently_played, user_name=user_name_data)


@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type':'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('/homepage')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)