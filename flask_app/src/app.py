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
from datetime import datetime, timedelta
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
from sql_work import SQLWork
from session_store import SessionStore
from load_gc import load_model
import csv

import random
from sklearn.metrics.pairwise import cosine_similarity
import time

import utils as utils
import re
# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False # Prevent jsonify from sorting keys in dict - Fix to top_ratios genre reordering

PROD = os.getenv('PROD')
if PROD == 'True':
    API_URL = os.getenv('API_URL')
else: 
    API_URL = 'http://localhost:3000'

print(API_URL, "latest")

CORS(app, supports_credentials=True, origins=[API_URL, "http://localhost:3000"])

app.secret_key = os.getenv('FLASK_SECRET_KEY')

@utils.log_memory_usage
def create_app():
    # global rec_dataset
    global playlist_vectors # Set up how to intermittently update during production runtime e.g. use Celery

    sql_work = SQLWork()

    session_store = SessionStore()
    
    playlist_vectors = sql_work.get_playlist_vectors()

    class_items = load_model()

    return app, sql_work, session_store, class_items

app, sql_work, session_store, class_items = create_app()


# Generate a random state string
def generate_random_string(length=16):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


@app.route('/auth/login')
@utils.log_memory_usage
def auth_login():
    print("Login route reached")
    scope = "streaming user-read-email user-read-private playlist-read-private playlist-read-collaborative user-top-read"
    state = generate_random_string()
    params = {
        'response_type': 'code',
        'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
        'scope': scope,
        'redirect_uri': f'{API_URL}/auth/callback', #5000 for production, 3000 for dev
        'state': state
    }
    url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return redirect(url)

@app.route('/auth/demo')
def auth_demo():
    print("Demo route reached")
    
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

    auth_opts = {
        'url' :  'https://accounts.spotify.com/api/token',
        "headers" : {
        'Authorization': f"Basic {client_creds_b64}",
        },
        'form': {
            'grant_type': 'client_credentials'
        },
        # "json" : true

    }
    response = requests.post(
        auth_opts['url'],
        headers=auth_opts['headers'],
        data=auth_opts['form']
    )
    
    print(f"Token exchange response: {response.status_code}, {response.text}")
    if response.status_code == 200:
        token_info = response.json()
        
        session['access_token'] = token_info.get('access_token')
        session['refresh_token'] = token_info.get('refresh_token')
        session['token_expires'] = datetime.now().timestamp() + token_info.get('expires_in')

        sp = SpotifyClient(Spotify(auth=session.get('access_token')))
        session['unique_id'], session['display_name'] = "31bv2bralifp3lgy4p5zvikjghki", "Demo User"
        unique_id = session.get('unique_id')    

        re = RecEngine(sp, unique_id, sql_work)

        user_top_tracks, user_top_artists = check_user_top_data_session(unique_id, re)

        return redirect(f'{API_URL}/')
    else:   
        return "Error in token exchange", response.status_code
        # unique_id, display_name = sql_work.get_user_data(sp)
        # start_time = time.time()
        # return jsonify({"access_token": access_token, "refresh_token": refresh, "expires": expires})
        

@app.route('/auth/callback')
@utils.log_memory_usage
def auth_callback():
    print("Callback route reached")
    code = request.args.get('code')
    state = request.args.get('state')
    # print(code, state)

    if not code:
        return "Error: No code in request", 400
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
        'redirect_uri': f'{API_URL}/auth/callback', #5000 for production, 3000 for dev
    }
    response = requests.post('https://accounts.spotify.com/api/token', data=auth_data, headers=auth_header)
    print(f"Token exchange response: {response.status_code}, {response.text}")
    if response.status_code == 200:
        token_info = response.json()
        session['access_token'] = token_info.get('access_token')
        session['refresh_token'] = token_info.get('refresh_token')
        session['token_expires'] = datetime.now().timestamp() + token_info.get('expires_in')

        start_time = time.time()
        
        sp = SpotifyClient(Spotify(auth=session.get('access_token')))
        unique_id, display_name = sql_work.get_user_data(sp)    
        session['unique_id'] = unique_id
        print(unique_id, "stored in session")
        session['display_name'] = display_name

        re = RecEngine(sp, unique_id, sql_work)

        # Check from SQL
        user_top_tracks, user_top_artists = check_user_top_data_session(unique_id, re)

        print("Login time:", time.time() - start_time)  
       
        # Redirecting or handling logic here
        return redirect(f'{API_URL}/')
    else:
        return "Error in token exchange", response.status_code

def is_token_expired():
    return datetime.now().timestamp() > session.get('token_expires', 0)
        
@app.route('/auth/token')
@utils.log_memory_usage
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
        return jsonify({'error': 'No token available'}), 401

@app.route('/auth/logout')
@utils.log_memory_usage
def logout():
    print("Logout route reached")
    session_store.remove_user_data(session.get('unique_id'))
    print("User data removed from session store")
    session.clear()
    response = jsonify({"message": "Logout successful"})
    response.status_code = 200
    print("Logout response:", response)
    return response

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

        should_recache = False
        if last_cached_str is None:
            print("Last cached user data not found, recaching")
            should_recache = True
        else:
            last_cached = datetime.fromisoformat(last_cached_str)
            should_recache = datetime.now() - last_cached > recache_threshold

        if should_recache:
            print("Recaching user data")
    
            re = RecEngine(sp, unique_id, sql_work)

            user_top_tracks, user_top_artists = check_user_top_data_session(unique_id, re)

            session['top_last_cached'] = datetime.now().isoformat()
            print(f"Updated last_cached to: {session['top_last_cached']}")

        return True
    else:
        return False

def check_user_top_data_session(unique_id, re):
    redis_key_top_tracks = f"{unique_id}:top_tracks"
    redis_key_top_artists = f"{unique_id}:top_artists"
    
    with utils.track_memory_usage("user_top_tracks memory"):
        user_top_tracks = session_store.get_data(redis_key_top_tracks)
    with utils.track_memory_usage("user_top_artists memory"):
        user_top_artists = session_store.get_data(redis_key_top_artists)
    if user_top_tracks:
        print("User top tracks found")
        ##Add recache function here
    else:
        print("User top tracks not found")
        with utils.track_memory_usage("re.get_user_top_tracks memory"):
            user_top_tracks = re.get_user_top_tracks()
        session_store.set_user_top_data(redis_key_top_tracks, user_top_tracks)
        print("User top tracks saved")
    if user_top_artists:
        print("User top artists found")
    else:
        print("User top artists not found")
        with utils.track_memory_usage("re.get_user_top_artists memory"):
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

def get_playlist_data_session(unique_id,link):
    if session.get('last_search') == link:
        p_features = session.get('p_features', {})
        if_public = p_features['privacy']
        redis_key_playlist = f"{unique_id}:{link}:{if_public}:playlist_vector"
        p_vector = session_store.get_data(redis_key_playlist)
        top_genres = session.get('top_genres')
        top_ratios = session.get('top_ratios')
        return p_vector, p_features, top_genres, top_ratios
    return None

def get_track_data_session(unique_id, link):
    if session.get('last_search') == link:
        redis_key_track = f"{unique_id}:{link}:track_vector"
        t_vector = session_store.get_data(redis_key_track)
        t_features = session.get('t_features', {})
        return t_vector, t_features
    return None

def save_playlist_data_session(unique_id, playlist, p_features, link, if_public, re, sp):
    p_vector = re.playlist_vector(playlist) # Get playlist vector
    # p_vector.to_csv('p_vector.csv', index=False)
    top_genres, top_ratios = re.get_top_genres(p_vector) # Getting from playlist vector returns weighted genre weights based on date added
    display_genres = get_display_genres(playlist)
    p_features.update({
        'display_genres': display_genres,
        'privacy': if_public
    })
    # Save playlist data to session
    redis_key_playlist = f"{unique_id}:{link}:{if_public}:playlist_vector"
    print(redis_key_playlist)

    if if_public == 'public':
        start_time = time.time()
        sql_work.add_vector_to_db(p_vector, link)
        print("Time to add vector to db:", time.time() - start_time)

    session_store.set_vector(redis_key_playlist, p_vector)
    session['top_genres'] = top_genres # To send as names to front end 
    session['top_ratios'] = top_ratios
    session['last_search'] = link 
    session['p_features'] = p_features

    print('Playlist data saved to session')
    return p_vector, p_features, top_genres, top_ratios,

def save_track_data_session(unique_id, track, t_features, link, re, sp):
    t_vector = re.track_vector(track) # Get track vector
    
    # Save track data to session
    redis_key_track = f"{unique_id}:{link}:track_vector"
    session_store.set_vector(redis_key_track, t_vector)
    session['t_features'] = t_features 
    session['last_search'] = link
    return t_vector, t_features

def get_display_genres(playlist, dominance_threshold=0.6, secondary_threshold=0.15, minimum_threshold=0.9, similarity_threshold=0.05):
    genre_counts = playlist['track_genre'].value_counts()
    genre_ratios = genre_counts / len(playlist)
    top_ratios = genre_ratios.head(3).to_dict()
    sorted_ratios = sorted(top_ratios.items(), key=lambda x: x[1], reverse=True) # Return largest ratio first
    display_genres = []

    for i, (genre, ratio) in enumerate(sorted_ratios):
        print(f"Processing genre {i+1}: {genre} - {ratio}")
        display_genres.append((genre, ratio))

        # Check if this genre close to the previous one
        if i > 0 and abs(ratio - display_genres[i-1][1]) <= similarity_threshold: # If difference between ratios < 0.05 // Access previous ratio
            print(f"Genre {i+1} is close to genre {i}")
            continue # Continue without returning 

        if i == 0 and ratio >= dominance_threshold: 
            print("Display Genres:", {genre: ratio})    
            return {genre: ratio}

        if i == 1 and ratio < secondary_threshold and abs(ratio - display_genres[0][1]) > similarity_threshold: 
            print(f"Second genre ({genre}) is not significant (<{secondary_threshold}) and not similar to first")
            
            return dict([display_genres[0]]) # Return first, as others insignificant

        if i == 2:
            if ratio < minimum_threshold and abs(ratio - display_genres[1][1]) > similarity_threshold: 
                print(f"Third genre ({genre}) is not significant (<{minimum_threshold}) and not similar to second")
                return dict(display_genres[:2])
            else:
                print("All three genres significant or similar in representation")
                return dict(display_genres) # Return all 3 genres if no criteria was met

    return dict(display_genres) # Return all genres if reached

def assert_lyds(unique_id, query):
    unique_id = session.get('unique_id')
    month_pattern = r"o[cv]t?ober"  
    day_pattern = r"29(th|st|nd|rd)?"  
    
    # Combine patterns for full date check
    full_pattern = f"^{month_pattern}\s*{day_pattern}$"
    query = query.lower()
    # Check for numeric format (10/29)
    if query == "10/29":
        if sql_work.assert_hers(unique_id):
            return "10/29"
    elif query == "ily!" or query == "i love you" or query == "i love you!" or query == "ily": 
            if sql_work.assert_hers(unique_id):
                return "ily"
    return False



@app.route('/t4/recommend', methods=['POST'])
@utils.log_memory_usage
def recommend():
    start_finish_time = time.time()
    # Check if the access token is expired and refresh if necessary
    if is_token_expired():
        if not refresh_token():
            return redirect('/auth/login')

    sp = SpotifyClient(Spotify(auth=session.get('access_token'))) # Initialize SpotifyClient
    unique_id = session.get('unique_id')

    re = RecEngine(sp, unique_id, sql_work)
  

    saved_playlists_ids = request.json.get('userPlaylistIds')
    print(f"Length of user saved playlists: {len(saved_playlists_ids)}")

    link = request.args.get('link')
    lyds = assert_lyds(unique_id, link)

    if lyds == "10/29":
        return jsonify('10/29'), 200 
    elif lyds == "ily":
        return jsonify('ily'), 200


    # saved_playlists = request.json.get('playlists')
    if not link:
        return jsonify({'error': 'No link provided'}), 400 # Cannot process request
    
    if '/' in link:
        # Extract the type and ID from the link
        # type_id = link.split('/')[3]
        link = link.split('/')[-1].split('?')[0]
        type_id, data = sp.get_id_type(link)
        session['type_id'] = type_id
    else:
        if session.get('type_id') is not None and session.get('last_search') == link:
            print("Type ID exists in session", session.get('type_id'))
            type_id = session.get('type_id')
        else:
            type_id, data = sp.get_id_type(link)
            session['type_id'] = type_id

    rec_redis_key = f'{unique_id}:{link}:{type_id}'
    # print(rec_redis_key)
    
    user_top_tracks, user_top_artists = check_user_top_data_session(unique_id, re)

    if type_id == 'playlist':
        # Check if playlist data exists in session
        playlist_data = get_playlist_data_session(unique_id, link)
        if playlist_data:
            print('Playlist data exists')
            p_vector, p_features, top_genres, top_ratios = playlist_data
            stored_recommendations = session_store.get_data(rec_redis_key)
            track_ids = stored_recommendations['track_ids']
            previously_recommended = stored_recommendations['recommended_ids']
            prev_p_rec_ids = stored_recommendations['playlist_rec_ids']
        else:
            print('Saving playlist data to session')
            playlist = data
            previously_recommended = []
            prev_p_rec_ids = []
            p_features = sp.playlist_base_features(playlist)
            playlist = sp.predict(playlist, type_id, class_items)
            track_ids = set(playlist['id'])

            p_features.update({
                'num_tracks': len(track_ids),
                'total_duration_ms': int(playlist['duration_ms'].sum()),
                'avg_popularity': playlist['popularity'].mean(),
            })

            if data['public']:
                if_public = 'public'
            else:
                if_public = 'private'

            # append_to_dataset(playlist, type_id) # Append Playlist songs to dataset
            p_vector, p_features, top_genres, top_ratios = save_playlist_data_session(unique_id, playlist, p_features, link, if_public, re, sp) # Save Playlist data to session
           
            print("Line 422, top ratios:", top_ratios)
            if len(track_ids) > 30: 
                session_store.update_trending_genres(top_ratios)
                # trending_genres = session_store.get_trending_genres()
                # print(trending_genres)

        recommended_ids = re.recommend_by_playlist(p_vector, track_ids, user_top_tracks, user_top_artists, class_items, top_genres, top_ratios, previously_recommended)
            
        print("Length of user saved playlist ids:", len(saved_playlists_ids)) # Why is nothing here? 
        playlist_rec_ids = re.recommend_playist_to_playlist(link, p_vector, playlist_vectors, saved_playlists_ids, prev_p_rec_ids)


    elif type_id == 'track':
        # Check if track data exists in session
        track_data = get_track_data_session(unique_id, link)
        if track_data:
            print('Track data exists')
            t_vector, t_features = track_data
            stored_recommendations = session_store.get_data(rec_redis_key)
            track_ids = stored_recommendations['track_ids']
            previously_recommended = stored_recommendations['recommended_ids']
            prev_p_rec_ids = stored_recommendations['playlist_rec_ids']
        else:
            print('Saving track data to session')
            previously_recommended = []
            prev_p_rec_ids = []
            track = data
            track, t_features = sp.track_base_features(track, link) 
            # track.to_csv('track.csv', index=False)
            track = sp.predict(track, type_id, class_items)
            track_ids = [link]

            print(track['track_genre'])

            t_features.update({ 
                'total_duration_ms': int(track['duration_ms']),
            })
            
            # append_to_dataset(track, type_id) # Append Track to dataset
            
            t_vector, t_features = save_track_data_session(unique_id, track, t_features, link, re, sp) # Save Track data to session
               
        # Get recommendations
        recommended_ids = re.recommend_by_track(t_vector, track_ids, user_top_tracks, class_items, previously_recommended)
        
        start_time =  time.time()
        playlist_rec_ids = re.recommend_playist_to_playlist(link, t_vector, playlist_vectors, saved_playlists_ids, prev_p_rec_ids)
        print("Time taken to get playlist recommendations:", time.time() - start_time)

    # Update recommended songs in session
    updated_recommendations = set(previously_recommended).union(set(recommended_ids))
    print("Length of updated_recommendations:", len(updated_recommendations))


    updated_playlist_recommendations = set(prev_p_rec_ids).union(set(playlist_rec_ids))
    prev_rec = {
        'track_ids': list(track_ids),
        'recommended_ids': list(updated_recommendations),
        'playlist_rec_ids': list(updated_playlist_recommendations),
    }
    session_store.set_prev_rec(rec_redis_key, prev_rec) # Update prev rec for user

    session_store.set_random_recs(list(updated_recommendations)) # Update random recs app wide
    # memory_usage = session_store.get_memory_usage(rec_redis_key)
    # print("Memory usage:", memory_usage, "bytes") 
    # stored_recommendations = session_store.get_data(rec_redis_key)
    # if stored_recommendations:
    #     track_ids = stored_recommendations['track_ids']
    #     prev_rec = stored_recommendations['recommended_ids']
    #     duplicate_strings = len(set(prev_rec)) != len(prev_rec)
    #     prev_rec_df = pd.DataFrame(prev_rec, columns=['prev_recommended_ids'])
    #     print("Duplicate strings in recommended_ids:", duplicate_strings)
    #     print("Length of track_ids:", len(track_ids))
    #     print("Length of recommended_ids:", len(prev_rec))
    #     print("Length of playlist rec ids:", len(updated_playlist_recommendations))
    # else:
    #     print("Stored recommendations not found")
        
    start_time = time.time()
    session_store.update_total_recs(len(recommended_ids))


    print("Time taken to update user recommendation count:", time.time() - start_time)
    print("Time taken to get recommendations:", time.time() - start_finish_time)


    if type_id == 'playlist':
        return jsonify({
            'p_features': p_features,
            'top_genres': top_genres,
            'recommended_ids': recommended_ids,
            'playlist_rec_ids': playlist_rec_ids,
            'id': link,
        })
    elif type_id == 'track':
        return jsonify({
            't_features': t_features,
            'recommended_ids': recommended_ids,
            'playlist_rec_ids': playlist_rec_ids,
            'id': link
        })

@app.route('/t4/search', methods=['GET'])
def autocomplete_playlist():
    unique_id = session.get('unique_id')
    playlists = sql_work.get_unique_user_playlist(unique_id)
    return jsonify(playlists)

@app.route('/t4/user', methods=['GET'])
def get_user_data():
    unique_id = session.get('unique_id')
    display_name = session.get('display_name')
    return jsonify({'unique_id': unique_id, 'display_name': display_name})

@app.route('/t4/total-recommendations', methods=['GET'])
def get_total_recommendations():
    total_recommendations, hourly_recs = session_store.get_total_recs()
    print("Total recommendations:", total_recommendations, "Hourly recommendations:", hourly_recs)
    return jsonify([total_recommendations, hourly_recs])

@app.route('/t4/random-recommendations', methods=['GET'])
def get_random_recommendations():
    random_recs = session_store.get_random_recs()
    return jsonify(random_recs)

@app.route('/t4/trending-genres', methods=['GET'])
def get_trending_genres():
    trending_genres = session_store.get_trending_genres()
    if len(trending_genres) == 0:
        trending_genres = None
    return jsonify(trending_genres)


def populate_seed_playlist_recs(sp, re):
    seed_playlists = []
    with open('../data/datasets/seed_playlists.csv', newline='') as f:
        for line in f:
            clean_line = line.strip().rstrip(',')
            if clean_line:
                seed_playlists.append(clean_line)

    for seed in seed_playlists:
        link = seed
        link = link.split('/')[-1].split('?')[0]
    
        type_id, data = sp.get_id_type(link)

        playlist = data
        playlist = sp.predict(playlist, type_id, class_items)
        p_vector = re.playlist_vector(playlist) # Get playlist vector
        start_time = time.time()
        sql_work.add_vector_to_db(p_vector, link)
        print(f"Time to add {link}-vector to db:", time.time() - start_time)
    

@app.route('/test') ### Keep for testing new features
def test():
    # if is_token_expired():
    #     if not refresh_token():
    #         return redirect('/auth/login')
    # unique_id: str = session.get('unique_id')
    # access_token: str = session.get('access_token')

    # # # Create Spotify client and RecEngine instance
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

    auth_opts = {
        'url' :  'https://accounts.spotify.com/api/token',
        "headers" : {
        'Authorization': f"Basic {client_creds_b64}",
        },
        'form': {
            'grant_type': 'client_credentials'
        },
        # "json" : true

    }
    response = requests.post(
        auth_opts['url'],
        headers=auth_opts['headers'],
        data=auth_opts['form']
    )
    
    print(f"Token exchange response: {response.status_code}, {response.text}")
    if response.status_code == 200:
        token_info = response.json()
        
        # session['access_token'] = token_info.get('access_token')
        # session['refresh_token'] = token_info.get('refresh_token')
        # session['token_expires'] = datetime.now().timestamp() + token_info.get('expires_in')

        access_token = token_info.get('access_token')
        refresh = token_info.get('refresh_token')
        expires = datetime.now().timestamp() + token_info.get('expires_in')
        start_time = time.time()
        return jsonify({"access_token": access_token, "refresh_token": refresh, "expires": expires})
        
    # redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
    # user_id = os.getenv("SPOTIFY_USER_ID")
    # scope = "streaming user-read-email user-read-private user-follow-read playlist-read-private playlist-read-collaborative user-read-recently-played user-library-read user-top-read"

    # auth_manager = SpotifyOAuth(client_id=client_id,
    #                             client_secret=client_secret,
    #                             redirect_uri=redirect_uri,
    #                             scope=scope,
    #                             username=user_id)
    # sp = spotipy.Spotify(auth_manager=auth_manager)
    # sp = SpotifyClient(Spotify(auth_manager=auth_manager)) # Initialize SpotifyClient
    # playlists = sp.user_playlists('spotify')
    # re = RecEngine(sp, unique_id, sql_work)

    # playlists=playlists[:5]
    return {"test":"failed"}
    


if __name__ == '__main__':
    if PROD == 'True':
        app.run(host='127.0.0.1', port=5000)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)

    # host='0.0.0.0', port=5000, debug=True
