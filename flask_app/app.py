from flask import Flask, request, redirect, session, jsonify
from flask_cors import CORS
import json
import os
import pandas as pd
import requests
import base64
from urllib.parse import urlencode
import string
import random
from dotenv import load_dotenv
import spotipy 
from spotipy import Spotify
from spotify_client import SpotifyClient
from rec_engine import RecEngine
from genre_class import GenreClassifier
from datetime import datetime
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
from sql_work import SQLWork






# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Set a secret key for session management
app.secret_key = os.getenv('FLASK_SECRET_KEY')

sql_work = SQLWork()
# Initialize Genre Class Model
gc = GenreClassifier() #// Pass in DF
model, scaler, label_encoder, X_train = gc.load_model()
# REC_DATASET_PATH = 'data/datasets/rec_dataset.csv'
# rec_dataset = pd.read_csv(REC_DATASET_PATH)
# append_data = pd.read_csv('data/datasets/append_data.csv')
global rec_dataset


# Generate a random state string
def generate_random_string(length=16):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


@app.route('/auth/login')
def auth_login():
    scope = "streaming user-read-email user-read-private user-follow-read playlist-read-private playlist-read-collaborative user-read-recently-played user-library-read user-top-read"
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
        session['refresh_token'] = token_info.get('refresh_token')
        session['token_expires'] = datetime.now().timestamp() + token_info.get('expires_in')
        
        sp = SpotifyClient(Spotify(auth=session.get('access_token')))
        unique_id, display_name = sql_work.get_user_data(sp)
        session['unique_id'] = unique_id
        session['display_name'] = display_name
        
        
        # Redirecting or handling logic here
        return redirect('/')
    else:
        return "Error in token exchange", response.status_code

def is_token_expired():
    return datetime.now().timestamp() > session.get('token_expires', 0)
        
@app.route('/auth/token')
def get_token():
    access_token = session.get('access_token')
    refresh_token = session.get('refresh_token')
    token_expires = session.get('token_expires')
    token_realexpire = session.get('token_realexpire')
    if access_token:
        return jsonify({'access_token': access_token, 
                        'refresh_token': refresh_token,
                        'token_expires': token_expires})

@app.route('/auth/logout')
def clear_session():

    session.clear()
    return "Session data cleared"





def refresh_token():
    if 'refresh_token' not in session:
        return False

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
        'grant_type': 'refresh_token',
        'refresh_token': session['refresh_token']
    }

    response = requests.post('https://accounts.spotify.com/api/token', data=auth_data, headers=auth_header)
    if response.status_code == 200:
        new_token_info = response.json()
        session['access_token'] = new_token_info.get('access_token')
        session['token_expires'] = datetime.now().timestamp() + new_token_info.get('expires_in')
        return True
    else:
        return False


# Append Data to rec_dataset
def append_to_dataset(data, choice):
    new_data = data.copy()
    if choice == 'track':
        new_data.drop('release_date', axis=1, inplace=True)  # Remove 'release_date' column if choice is 'track'
    elif choice == 'playlist':
        new_data.drop('date_added', axis=1, inplace=True)  # Remove 'date_added' column if choice is 'playlist'
    new_data.rename(columns={'artist': 'artists', 'name': 'track_name', 'id': 'track_id'}, inplace=True)  # Rename columns
    append_counter = session['append_counter']
    append = sql_work.append_tracks(new_data, append_counter)
    if append:
        session['append_counter'] = 0


def get_playlist_data_session(link):
    if session.get('last_search') == link and 'playlist_name' in session:
        print('Playlist session data exists')
        p_vector = session.get('p_vector')
        p_vector = pd.read_json(p_vector, orient='records')
        playlist_name = session.get('playlist_name')
        top_genres = session.get('top_genres')
        previously_recommended = session.get('recommended_songs', [])
        print(previously_recommended) #
        return p_vector, playlist_name, top_genres, previously_recommended
    return None

def get_track_data_session(link):
    if session.get('last_search') == link and 'track_name' in session:
        print('Track session data exists')
        t_vector = session.get('t_vector')
        t_vector = pd.read_json(t_vector, orient='records')
        track_name = session.get('track_name')
        artist_name = session.get('artist_name')
        release_date = session.get('release_date')
        track_id = session.get('track_id')
        previously_recommended = session.get('recommended_songs', [])
        return t_vector, track_name, artist_name, release_date, track_id, previously_recommended
    return None

def save_playlist_data_session(playlist, link, re, sp):
    p_vector = re.playlist_vector(playlist) # Get playlist vector
    playlist_name = sp.get_playlist_track_name(link) # Get playlist name
    top_genres = re.get_top_genres(p_vector) # Get top genres
    playlist_ids = playlist['id'].tolist() # Get playlist track IDs
    p_vector_json = p_vector.to_json(orient='records') # Convert playlist vector to JSON
    top_genres = top_genres.tolist() 
    # Save playlist data to session
    session['p_vector'] = p_vector_json 
    session['playlist_name'] = playlist_name 
    session['top_genres'] = top_genres  
    session['last_search'] = link 
    print('Playlist data saved to session')
    return p_vector, playlist_name, top_genres

def save_track_data_session(track, link, re, sp):
    track_id = track['id'].tolist() # Get track ID
    track_name, artist_name, release_date = sp.get_playlist_track_name(link, 'track') # Get track name, artist name, and release date
    t_vector = re.track_vector(track) # Get track vector
    t_vector_json = t_vector.to_json(orient='records') # Convert track vector to JSON
    # Save track data to session
    session['t_vector'] = t_vector_json
    session['track_name'] = track_name
    session['artist_name'] = artist_name
    session['release_date'] = release_date
    session['track_id'] = track_id
    session['last_search'] = link
    return t_vector, track_name, artist_name, release_date, track_id

@app.route('/recommend', methods=['GET'])
def recommend():

    # Check if the access token is expired and refresh if necessary
    if is_token_expired():
        if not refresh_token():
            return redirect('/auth/login')

    sp = SpotifyClient(Spotify(auth=session.get('access_token'))) # Initialize SpotifyClient

    link = request.args.get('link')
    if not link:
        return jsonify({'error': 'No link provided'}), 400 # Cannot process request

    # Extract the type and ID from the link
    type_id = link.split('/')[3]
    link = link.split('/')[-1].split('?')[0]

    if type_id == 'playlist':
        # Check if playlist data exists in session
        playlist_data = get_playlist_data_session(link)
        if playlist_data:
            print('Playlist data exists')
            p_vector, playlist_name, top_genres, previously_recommended = playlist_data
            re = RecEngine(sp, previously_recommended=previously_recommended)
        else:
            print('Playlist data does not exist')
            previously_recommended = session['recommended_songs'] = []
            re = RecEngine(sp, previously_recommended=previously_recommended)  
            playlist = sp.predict(link, type_id, model, scaler, label_encoder, X_train)

            session['append_counter'] = session.get('append_counter', 0) + 1
            print("Append counter:", session['append_counter'])

            
            append_to_dataset(playlist, type_id) # Append Playlist songs to dataset
            p_vector, playlist_name, top_genres = save_playlist_data_session(playlist, link, re, sp) # Save Playlist data to session
        
        # Get recommendations
        recommended_ids = re.recommend_by_playlist(rec_dataset, p_vector, link)

    elif type_id == 'track':
        # Check if track data exists in session
        track_data = get_track_data_session(link)
        if track_data:
            t_vector, track_name, artist_name, release_date, track_id, previously_recommended = track_data
            re = RecEngine(sp, previously_recommended=previously_recommended)
        else:
            previously_recommended = session['recommended_songs'] = []
            re = RecEngine(sp, previously_recommended=previously_recommended) 
            track = sp.predict(link, type_id, model, scaler, label_encoder, X_train)
            
            session['append_counter'] = session.get('append_counter', 0) + 1
            print("Append counter:", session['append_counter'])

            # Append Track to dataset
            append_to_dataset(track, type_id)
            
            t_vector, track_name, artist_name, release_date, track_id = save_track_data_session(track, link, re, sp) # Save Track data to session
        
        # Get recommendations
        recommended_ids = re.recommend_by_track(rec_dataset, t_vector, track_id)

    # Update recommended songs in session
    updated_recommendations = set(previously_recommended).union(set(recommended_ids))
    session['recommended_songs'] = list(updated_recommendations)


    if type_id == 'playlist':
        return jsonify({
            'playlist': playlist_name,
            'top_genres': top_genres,
            'recommended_ids': recommended_ids
        })
    elif type_id == 'track':
        return jsonify({
            'track': track_name,
            'artist': artist_name,
            'release_date': release_date,
            'recommended_ids': recommended_ids
        })

@app.route('/search', methods=['GET'])
def autocomplete_playlist():

    unique_id = session.get('unique_id')
    playlists = sql_work.get_unique_user_playlist(unique_id)
    return jsonify(playlists)


    

if __name__ == '__main__':
    global rec_dataset
    sql_work.connect_sql()
    rec_dataset = sql_work.get_dataset()
    app.run(debug=True)
