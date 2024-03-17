import os
import time
import pandas as pd
from dotenv import load_dotenv
from spotify_client import SpotifyClient
from genre_class import GenreClassifier
from rec_engine import RecEngine
import logging


REC_DATASET_PATH = 'data/rec_dataset.csv'
rec_dataset = pd.read_csv(REC_DATASET_PATH)
#REC_OHE_PATH = 'data/rec_ohe.csv'

def load_environment_variables():
    load_dotenv()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    user_id = os.getenv("SPOTIFY_USER_ID")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
    scope ='playlist-read-private user-library-read'
    return client_id, client_secret, redirect_uri, user_id, scope

def initialize_spotify_client(client_id, client_secret, redirect_uri, user_id, scope):
    return SpotifyClient(client_id, client_secret, redirect_uri, user_id, scope)

def initialize_genre_classifier(sp):
    return GenreClassifier(REC_DATASET_PATH, sp)

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
    gc.load_model()
    while True:
        try:
            playlist_id = input("\nPlease enter the link of the playlist you would like recommendations for, or exit: ")
            if playlist_id.lower() == "exit":
                return
            playlist_id = playlist_id.split('/')[-1].split('?')[0]
            playlist = gc.predict(playlist_id)  # Assuming 0 is the correct recommend_type
            playlist.to_csv('playlist.csv', index=False)
            p_vector, final_rec_df = re.playlist_vector(playlist, rec_dataset)
        except Exception as e:
            print("Error retrieving playlist. Please try entering the playlist link again.")
            continue  # Skip to the next iteration of the loop to ask for a new playlist link
        
        playlist_name = sp.get_playlist_name(playlist_id)
        top_genres = re.get_top_genres(p_vector)
        print(f"\n{playlist_name} is a {', '.join(top_genres)} playlist.\nHere are some recommendations that you might like, both in and out of your genre.")

        while True:
            recommendations = re.recommend(rec_dataset, p_vector, final_rec_df)
            print()
            print(recommendations)
            more_recs = input("Do you want more recommendations? (yes/no): ")
            if more_recs.lower() != "yes":
                new_playlist = input("Do you want to try recommendations on a new playlist? (yes/no): ")
                if new_playlist.lower() == "yes":
                    break  # Break the inner loop to go back to asking for a new playlist link
                else:
                    return

def main():
    client_id, client_secret, redirect_uri, user_id, scope = load_environment_variables()
    sp = initialize_spotify_client(client_id, client_secret, redirect_uri, user_id, scope)
    re = RecEngine(sp)
    gc = initialize_genre_classifier(sp)
    generate_recommendations(gc, re, sp)

    # playlist_id = input("\nPlease enter the link: ")
    # if playlist_id.lower() == "exit":
    #     return
    # playlist_id = playlist_id.split('/')[-1].split('?')[0]
    # print(sp.get_id_type(playlist_id))
    #print(sp.analyze_playlist('7e0q9fqr1IpUKQlH0AVzzl'))
    # df = pd.read_csv('top_recommendations.csv')
    # print(sp.get_track_links(df))




if __name__ == "__main__":
    main()