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
from datetime import datetime, timedelta
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
from sql_work import SQLWork
from session_store import SessionStore

import random
from sklearn.metrics.pairwise import cosine_similarity
import time


# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False # Prevent jsonify from sorting keys in dict - Fix to top_ratios genre reordering

CORS(app, supports_credentials=True, origins="http://localhost:3000")


app.secret_key = os.getenv('FLASK_SECRET_KEY')

sql_work = SQLWork()
session_store = SessionStore()
# Initialize Genre Class Model
# gc = GenreClassifier()
# class_items = gc.load_model()

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
        print(unique_id, "stored in session")
        session['display_name'] = display_name

        re = RecEngine(sp, unique_id, sql_work)

        # Re-evaluate if this needs to be recalculated each time
        user_top_tracks, user_top_artists = check_user_top_data_session(unique_id, re)
       
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
    else:
        return jsonify({'error': 'No token available'})

@app.route('/auth/logout')
def logout():
    unique_id = session.get('unique_id')
    session.clear()
    session_store.clear_user_cache(unique_id)
    session_store.remove_user_data(unique_id)

    return jsonify({access_token: None, refresh_token: None, token_expires: None})

def refresh_token():
    if 'refresh_token' not in session:
        return False
    print("-> app.py:refresh_token()")
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
        sp = SpotifyClient(Spotify(auth=session.get('access_token')))
        unique_id, display_name = sql_work.get_user_data(sp)
        session['unique_id'] = unique_id
        session['display_name'] = display_name

        recache_threshold = timedelta(days=1)
        last_cached_str = session.get('top_last_cached')

        if last_cached_str is None:
            last_cached = None
        else:
            last_cached = datetime.fromisoformat(last_cached_str)
        
        if last_cached is None or datetime.now() - last_cached > recache_threshold:

            re = RecEngine(sp, unique_id, sql_work)

            user_top_tracks, user_top_artists = check_user_top_data_session(unique_id, re)

        return True
    else:
        return False



def check_user_top_data_session(unique_id, re):
    redis_key_top_tracks = f"{unique_id}_top_tracks"
    redis_key_top_artists = f"{unique_id}_top_artists"
    user_top_tracks = session_store.get_data(redis_key_top_tracks)
    user_top_artists = session_store.get_data(redis_key_top_artists)
    if user_top_tracks:
        print("User top tracks found")
        ##Add recache function here
    else:
        print("User top tracks not found")
        user_top_tracks = re.get_user_top_tracks()
        session_store.set_user_top_data(redis_key_top_tracks, user_top_tracks)
        print("User top tracks saved")
    if user_top_artists:
        print("User top artists found")
    else:
        print("User top artists not found")
        user_top_artists = re.get_user_top_artists()
        session_store.set_user_top_data(redis_key_top_artists, user_top_artists)
        print("User top artists saved")
    return user_top_tracks, user_top_artists


# Append Data to rec_dataset
def append_to_dataset(data, choice):
    session['append_counter'] = session.get('append_counter', 0) + 1
    print("Append counter:", session['append_counter'])

    new_data = data.copy()
    if choice == 'track':
        new_data.drop('release_date', axis=1, inplace=True)  # Remove 'release_date' column if choice is 'track'
    elif choice == 'playlist':
        new_data.drop('date_added', axis=1, inplace=True)  # Remo   ve 'date_added' column if choice is 'playlist'
    new_data.rename(columns={'artist': 'artists', 'name': 'track_name', 'id': 'track_id'}, inplace=True)  # Rename columns
    append_counter = session['append_counter']
    start_time = time.time()
    append = sql_work.append_tracks(new_data, append_counter)
    print("Appended tracks in %s seconds", (time.time() - start_time))
    if append:
        session['append_counter'] = 0 

def get_playlist_data_session(link):
    if session.get('last_search') == link and 'playlist_name' in session:
        start_time = time.time()
        # p_vector = sql_work.get_vector_from_db(link, 'playlist')
        redis_key_playlist = f"{link}_playlist"
        p_vector = session_store.get_data_cache(redis_key_playlist)
        print("Grabbed playlist vector in %s seconds", (time.time() - start_time))
        playlist_name = session.get('playlist_name')
        top_genres = session.get('top_genres')
        top_ratios = session.get('top_ratios')
        print(top_ratios)
        return p_vector, playlist_name, top_genres, top_ratios
    return None

def get_track_data_session(link):
    if session.get('last_search') == link and 'track_name' in session:
        t_vector = sql_work.get_vector_from_db(link, 'track')
        track_name = session.get('track_name')
        artist_name = session.get('artist_name')
        release_date = session.get('release_date')
        return t_vector, track_name, artist_name, release_date
    return None

def save_playlist_data_session(playlist, link, re, sp):
    p_vector = re.playlist_vector(playlist) # Get playlist vector
    playlist_name = sp.get_playlist_track_name(link) # Get playlist name
    top_genres, top_ratios = re.get_top_genres(p_vector) # Get top genres
    playlist_ids = playlist['id'].tolist() # Get playlist track IDs
    # top_genres = top_genres.tolist() 

    # Save playlist data to session
    p_vector_dict = p_vector.to_dict(orient='records')[0]
    # sql_work.add_vector_to_db(p_vector_dict, link, 'playlist')
    redis_key_playlist = f"{link}_playlist"
    session_store.set_vector(redis_key_playlist, p_vector)
    session['playlist_name'] = playlist_name 
    session['top_genres'] = top_genres 
    session['top_ratios'] = top_ratios
    session['last_search'] = link 
    print('Playlist data saved to session')
    return p_vector, playlist_name, top_genres, top_ratios

def save_track_data_session(track, link, re, sp):
    track_name, artist_name, release_date = sp.get_playlist_track_name(link, 'track') # Get track name, artist name, and release date
    t_vector = re.track_vector(track) # Get track vector
    
    # Save track data to session
    t_vector_dict = t_vector.to_dict(orient='records')[0]
    sql_work.add_vector_to_db(t_vector_dict, link, 'track')
    session['track_name'] = track_name
    session['artist_name'] = artist_name
    session['release_date'] = release_date
    session['last_search'] = link
    return t_vector, track_name, artist_name, release_date

@app.route('/recommend', methods=['GET'])
def recommend():

    start_finish_time = time.time()
    # Check if the access token is expired and refresh if necessary
    if is_token_expired():
        if not refresh_token():
            return redirect('/auth/login')

    sp = SpotifyClient(Spotify(auth=session.get('access_token'))) # Initialize SpotifyClient
    unique_id = session.get('unique_id')
    re = RecEngine(sp, unique_id, sql_work)

    link = request.args.get('link')
    if not link:
        return jsonify({'error': 'No link provided'}), 400 # Cannot process request

    if '/' in link:
        # Extract the type and ID from the link
        type_id = link.split('/')[3]
        link = link.split('/')[-1].split('?')[0]
    else:
        type_id = 'playlist'

    redis_key = f'{unique_id}:{link}:{type_id}'
    print(redis_key)
    
    user_top_tracks, user_top_artists = check_user_top_data_session(unique_id, re)

    if type_id == 'playlist':
        # Check if playlist data exists in session
        playlist_data = get_playlist_data_session(link)
        if playlist_data:
            print('Playlist data exists')
            p_vector, playlist_name, top_genres, top_ratios = playlist_data
            stored_recommendations = session_store.get_data(redis_key)
            track_ids = stored_recommendations['track_ids']
            previously_recommended = stored_recommendations['recommended_ids']
            # re = RecEngine(sp, unique_id, sql_work)
        else:
            print('Saving playlist data to session')
            previously_recommended = []
            # re = RecEngine(sp, unique_id, sql_work)
            playlist = sp.predict(link, type_id, class_items)
            playlist.to_csv('playlist.csv', index=False)
            track_ids = set(playlist['id'])

            # append_to_dataset(playlist, type_id) # Append Playlist songs to dataset
            p_vector, playlist_name, top_genres, top_ratios = save_playlist_data_session(playlist, link, re, sp) # Save Playlist data to session
            print(top_ratios)
        
        recommended_ids = re.recommend_by_playlist(rec_dataset, p_vector, track_ids, user_top_tracks, user_top_artists, class_items, top_genres, top_ratios, previously_recommended)

    elif type_id == 'track':
        # Check if track data exists in session
        track_data = get_track_data_session(link)
        if track_data:
            print('Track data exists')
            t_vector, track_name, artist_name, release_date = track_data
            stored_recommendations = session_store.get_data(redis_key)
            track_ids = stored_recommendations['track_ids']
            previously_recommended = stored_recommendations['recommended_ids']
        else:
            print('Saving track data to session')
            previously_recommended = []
            track = sp.predict(link, type_id, class_items)
            track_ids = track['id'].tolist() # Get track ID
            
            # append_to_dataset(track, type_id) # Append Track to dataset
            
            t_vector, track_name, artist_name, release_date = save_track_data_session(track, link, re, sp) # Save Track data to session
               
        # Get recommendations
        recommended_ids = re.recommend_by_track(rec_dataset, t_vector, track_ids, user_top_tracks, class_items, previously_recommended)

    # Update recommended songs in session
    updated_recommendations = set(previously_recommended).union(set(recommended_ids))
    print("Length of updated_recommendations:", len(updated_recommendations))
    session_store.set_prev_rec(redis_key, list(track_ids), list(updated_recommendations))
    memory_usage = session_store.get_memory_usage(redis_key)
    print("Memory usage:", memory_usage, "bytes") 
    stored_recommendations = session_store.get_data(redis_key)
    if stored_recommendations:
        track_ids = stored_recommendations['track_ids']
        prev_rec = stored_recommendations['recommended_ids']
        duplicate_strings = len(set(prev_rec)) != len(prev_rec)
        prev_rec_df = pd.DataFrame(prev_rec, columns=['prev_recommended_ids'])
        print("Duplicate strings in recommended_ids:", duplicate_strings)
        print("Length of track_ids:", len(track_ids))
        print("Length of recommended_ids:", len(prev_rec))
    else:
        print("Stored recommendations not found")
    start_time = time.time()    
    sql_work.update_user_recommendation_count(unique_id, len(recommended_ids))
    print("Time taken to update user recommendation count:", time.time() - start_time)
    print("Time taken to get recommendations:", time.time() - start_finish_time)
    if type_id == 'playlist':
        return jsonify({
            'playlist': playlist_name,
            'top_genres': top_genres,
            'recommended_ids': recommended_ids,
            'id': link
        })
    elif type_id == 'track':
        return jsonify({
            'track': track_name,
            'artist': artist_name,
            'release_date': release_date,
            'recommended_ids': recommended_ids,
            'id': link
        })

@app.route('/search', methods=['GET'])
def autocomplete_playlist():
    unique_id = session.get('unique_id')
    playlists = sql_work.get_unique_user_playlist(unique_id)
    return jsonify(playlists)


@app.route('/user', methods=['GET'])
def get_user_data():
    unique_id = session.get('unique_id')
    display_name = session.get('display_name')
    access_token = session.get('access_token')
    sp = SpotifyClient(Spotify(auth=access_token))
    re = RecEngine(sp, unique_id, sql_work)
    check_user_top_data_session(unique_id, re)
    return jsonify({'unique_id': unique_id, 'display_name': display_name})

@app.route('/favorited', methods=['POST'])
def save_favorited():
    data = request.get_json()
    favorited_tracks = data.get('favoritedTracks', [])
    recommendation_id = data.get('recommendationID')
    if favorited_tracks:
        unique_id = session.get('unique_id')
        print(unique_id)
        sql_work.add_liked_tracks(unique_id, recommendation_id, favorited_tracks)
        return jsonify({'message': 'Favorited tracks saved successfully'})
    else:
        return jsonify({'message': 'No favorited tracks provided'})

@app.route('/test') ### Keep for testing new features
def test():
    unique_id: str = session.get('unique_id')
    access_token: str = session.get('access_token')

    # Create Spotify client and RecEngine instance
    sp = SpotifyClient(Spotify(auth=access_token))
    re = RecEngine(sp, unique_id, sql_work)

    session.clear()
    session_store.clear_user_cache(unique_id)
    session_store.remove_user_data(unique_id)
    # return user_top_tracks, user_top_artists

    # session_store.remove_user_data(unique_id)

    # top_tracks, top_artists = check_user_top_data_session(unique_id, re)

    # session_store.clear_user_cache(unique_id=unique_id)

    return jsonify("Logged out")    


if __name__ == '__main__':
    global rec_dataset
    sql_work.connect_sql()
    rec_dataset = sql_work.get_dataset()
    app.run(host="0.0.0.0", port=5000, debug=True)
