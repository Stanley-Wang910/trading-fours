import os
import time
import pandas as pd
from dotenv import load_dotenv
from spotify_client import SpotifyClient
from genre_class import GenreClassifier
from rec_engine import RecEngine
import mysql.connector



REC_DATASET_PATH = 'data/datasets/rec_dataset.csv'
# rec_dataset = pd.read_csv(REC_DATASET_PATH)
#REC_OHE_PATH = 'data/rec_ohe.csv'

def load_environment_variables():
    load_dotenv()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    user_id = os.getenv("SPOTIFY_USER_ID")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")
    cnx = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    rec_dataset = pd.read_sql("SELECT * FROM rec_dataset", cnx)
    rec_dataset = rec_dataset.drop('id', axis=1)
    # rec_dataset.to_csv('testrecdata.csv', index=False)



    scope ='playlist-read-private user-library-read'
    return client_id, client_secret, redirect_uri, user_id, scope, rec_dataset

def initialize_spotify_client(client_id, client_secret, redirect_uri, user_id, scope):
    return SpotifyClient(client_id, client_secret, redirect_uri, user_id, scope)

def initialize_genre_classifier():
    return GenreClassifier()

def train_genre_classifier(gc):
    gc.preprocess_data()
    gc.train_test_split()
    gc.train_save_model()

def generate_recommendations(gc, re, sp):
    global rec_dataset
    print("\nLoading Genre Classification", end="", flush=True)
    for _ in range(3):
        print(".", end="", flush=True)
        time.sleep(0.25)
    model, scaler, label_encoder, X_train = gc.load_model()
    while True:
        try:
            type_id = input("\nPlease enter the link of the playlist or track you would like recommendations for, or exit: ")
            if type_id.lower() == "exit":
                return
            type_id = type_id.split('/')[-1].split('?')[0]

            rec_type = sp.get_id_type(type_id)
            if rec_type == 'playlist':
                playlist = sp.predict(type_id, model, scaler, label_encoder, X_train) 
                # playlist.to_csv('playlist.csv', index=False)
                p_vector, final_rec_df = re.playlist_vector(playlist, rec_dataset)

            elif rec_type == 'track':
                track = sp.predict(type_id, model, scaler, label_encoder, X_train)
                t_vector, final_rec_df = re.track_vector(track, rec_dataset)
        except Exception as e:
            print(f"Error retrieving {rec_type}. Please try entering the {rec_type} link again.")
            continue  # Skip to the next iteration of the loop to ask for a new playlist link
        
        
        if rec_type == 'playlist':    
            playlist_name = sp.get_playlist_track_name(type_id)
            top_genres = re.get_top_genres(p_vector)
            print(f"\n{playlist_name} is a {', '.join(top_genres)} playlist.\nHere are some recommendations that you might like, both in and out of your genre.")

        elif rec_type == 'track':
            track_name, artist_name, release_date = sp.get_playlist_track_name(type_id, 'track')
        while True:
            if rec_type == 'playlist':
                recommendations = re.recommend_by_playlist(rec_dataset, p_vector, final_rec_df)
                print()
                print(recommendations)
            elif rec_type == 'track':
                era_choice = input(f'Would you be interested in discovering songs that were released in the same year ({release_date}) as {track_name} by {artist_name}? (yes/no): ')
                
                recommendations = re.recommend_by_track(rec_dataset, t_vector, final_rec_df, era_choice)
                print()
                print(recommendations)
            more_recs = input("Do you want more recommendations? (yes/no): ")
            if more_recs.lower() != "yes":
                new_playlist = input("Do you want to try recommendations on a new track/playlist? (yes/no): ")
                if new_playlist.lower() == "yes":
                    break  # Break the inner loop to go back to asking for a new playlist/track link
                else:
                    return

def main():
    client_id, client_secret, redirect_uri, user_id, scope, rec_dataset = load_environment_variables()
    sp = initialize_spotify_client(client_id, client_secret, redirect_uri, user_id, scope)
    re = RecEngine(sp)
    gc = initialize_genre_classifier()
    model, scaler, label_encoder, X_train = gc.load_model()

    track = sp.predict('5IMNH2wQ9Agbkp6uCoPpjs', 'track', model, scaler, label_encoder, X_train)
    track_vector = re.track_vector(track)
    track_vector.to_csv('track_vector.csv', index=False)
    top = re.recommend_by_track(rec_dataset, track_vector,  ['5IMNH2wQ9Agbkp6uCoPpjs'])
    print(top)
    
    # generate_recommendations(gc, re, sp)

    # try_this = sp.get_id_type('37i9dQZF1DX5Ejj0EkURtP')
    # print(try_this)
    
    


if __name__ == "__main__":
    main()