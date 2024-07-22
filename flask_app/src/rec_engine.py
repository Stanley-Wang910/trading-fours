import pandas as pd
import numpy as np
import time
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
from spotify_client import SpotifyClient

# ## for testing
# import os
# import sys
# ##


import random
import time


class RecEngine:
    # @staticmethod
    # def mute_print(*args, **kwargs):
    #     pass

    def __init__(self, spotify_client, unique_id, sql_cnx):
        self.sp = spotify_client
        self.unique_id = unique_id
        self.sql_cnx = sql_cnx
        # global print
        # print = self.mute_print
       

    def playlist_vector(self, playlist, weight=1.1):
        # print('-> re:playlist_vector()')
        # start_time = time.time()

        playlist = self.ohe_features(playlist)

        # Drop unnecessary columns from the playlist dataframe
        playlist = playlist.drop(columns=['artist', 'name', 'id'])

        # Calculate the most recent date in the playlist
        most_recent_date = playlist.iloc[0, 0]
        most_recent_date = pd.to_datetime(most_recent_date, unit='ms').tz_localize(None)

        if most_recent_date != pd.Timestamp('1970-01-01 00:00:00') or most_recent_date != 0: 
            # Calculate the number of months behind for each track in the playlist
            playlist['date_added'] = pd.to_datetime(playlist['date_added'], unit='ms').dt.tz_localize(None)
            playlist['months_behind'] = ((most_recent_date - playlist['date_added']).dt.days / 30).astype(int)

            # Calculate the weight for each track based on the months behind
            playlist['weight'] = weight ** (-playlist['months_behind'])
            playlist_df_weighted = playlist.copy()

            # Update the values in the playlist dataframe with the weighted values
            cols_to_update = playlist_df_weighted.columns.difference(['date_added', 'weight', 'months_behind'])
            playlist_df_weighted.update(playlist_df_weighted[cols_to_update].mul(playlist_df_weighted.weight, axis=0))

            weight_sum = playlist_df_weighted['weight'].sum()
            # Get the final playlist vector by excluding unnecessary columns
            playlist_vector = playlist_df_weighted[playlist_df_weighted.columns.difference(['date_added', 'weight', 'months_behind'])].sum(axis=0) / weight_sum
        else:
            # If the most recent date is the default value, exclude only the 'date_added' column
            playlist_vector = playlist.drop(columns=['date_added']).mean(axis=0)

        # Transposes into a one row vector
        playlist_vector = playlist_vector.to_frame().T

        # print(f'Playlist vector created in {time.time() - start_time:.2f} s')
        print('<- re:playlist_vector()')
        return playlist_vector

    def recommend_playist_to_playlist(self, playlist_id, p_vector, playlist_vectors, saved_playlist_ids, prev_p_rec_ids):
        print('-> re:recommend_playist_to_playlist()')

        # Filter out playlists in user saved playlists, so save the unique id in these vectors
        
        columns_to_drop = ['duration_ms', 'popularity']
        p_vector.drop(columns=[col for col in columns_to_drop if col in p_vector.columns], axis=1, inplace=True)
        playlist_vectors.drop(columns=[col for col in columns_to_drop if col in playlist_vectors.columns], axis=1, inplace=True)
        
        playlist_vectors = playlist_vectors[~playlist_vectors['playlist_id'].isin([playlist_id] + saved_playlist_ids + prev_p_rec_ids)]

        playlist_vectors_no_id = playlist_vectors.drop(columns=['playlist_id'])

        playlist_vectors['similarity'] = cosine_similarity(playlist_vectors_no_id.values, p_vector.values.reshape(1, -1))[:,0]

        playlist_vectors = playlist_vectors.sort_values(by='similarity', ascending=False)
        # Return the top 10 results playlist_id

        print('<- re:recommend_playist_to_playlist()')
        # Introduce a random element
        return playlist_vectors['playlist_id'].head(9).tolist()   # .sample(5).tolist()



    def recommend_by_playlist(
        self,
        rec_dataset,
        playlist_vector,
        p_track_ids,
        user_top_tracks,
        user_top_artists,
        class_items,
        top_genres,
        top_ratios,
        recommended_ids=[]
    ):
        """
        Recommend songs based on a playlist.
        """
        print('-> re:recommend_by_playlist()')

        # Prepare data for recommendation
        playlist_vector, rec_dataset, ohe_rec_dataset, top_artists_tracks, ohe_top_artist_tracks = self.prepare_data(
            self.sp,
            rec_dataset,
            playlist_vector,
            p_track_ids,
            recommended_ids,
            [artist['artist_name'] for artist in user_top_artists] # user_top_artists names
        )

        # Apply weights to the top genres
        weights = self.create_weights(top_genres, top_ratios)
        ohe_rec_dataset = self.apply_weights(ohe_rec_dataset, weights)

        # Find similar artists
        top_3_artists = self.find_similar_artists(
            top_artists_tracks,
            ohe_top_artist_tracks,
            playlist_vector,
            top_genres,
            top_ratios,
            weights
        )
        print("Top 3 Artists:", top_3_artists)
        if top_3_artists:
            artist_recs = self.get_artist_recs(
                rec_dataset,
                top_3_artists, 
                user_top_artists, 
                playlist_vector, 
                p_track_ids, 
                recommended_ids, 
                weights
            )

        # Get personalized vector
        personalized_vector = self.get_personalized_vector(
            playlist_vector,
            weights,
            user_top_tracks,
            class_items
        )

        # Combine vectors
        combined_vector = 0.7 * playlist_vector + 0.3 * personalized_vector

        # Calculate similarity between combined and rec_dataset, return with ranked similarity
        rec_dataset = self.calc_cosine_similarity(
            rec_dataset,
            ohe_rec_dataset,
            combined_vector,
            weights
        )

        # Initialize an empty DataFrame to store top songs
        top_songs = pd.DataFrame()

        print("Selecting top songs...")
        # Select top songs from each genre based on similarity and add them to the top_songs DataFrame
        for genre in top_genres:
            genre_songs = rec_dataset[rec_dataset['track_genre'] == genre]
            top_songs = pd.concat(
                [top_songs, genre_songs.nlargest(90 // len(top_genres), 'similarity')]
            )

        # If no songs are found, return an empty list
        if top_songs.empty:
            return []

        # Finalize and update the recommended songs
        recommendations = self.finalize_update_recommendations(
            top_songs,
            'playlist',
            artist_recs,
            top_ratios
        )

        return recommendations

    def get_artist_recs(
        self, 
        rec_dataset,
        top_3_artists, 
        user_top_artists, 
        playlist_vector, 
        p_track_ids, 
        recommended_ids, 
        weights
    ):
        """
        Recommend songs based on similar & related artists
        """
        print('-> re:get_artist_recs()')
        # start_time = time.time()

        # Get IDs of user's top 3 artists
        top_artist_ids = [
            artist['artist_id']
            for artist in user_top_artists
            if artist['artist_name'] in top_3_artists
        ]
        # Get artists related to the top 3 artists
        related_artists = self.get_related_artists(
            top_artist_ids,
            [artist['artist_name'] for artist in user_top_artists], # user_top_artists names
            user_top_artists
        )

        print("Related Artists:", related_artists)

        # Get related artist tracks
        related_artists_tracks = rec_dataset[rec_dataset['artists'].isin(related_artists)]
        _, related_artists_tracks, related_artists_tracks_ohe = self.prepare_data(
            self.sp,
            related_artists_tracks,
            playlist_vector,
            p_track_ids,
            recommended_ids
        )

        # Calculate cosine similarity between final playlist vector and related artist tracks to find 
        related_artists_tracks_ohe = self.apply_weights(related_artists_tracks_ohe, weights)
        artist_recs_df = self.calc_cosine_similarity(
            related_artists_tracks,
            related_artists_tracks_ohe,
            playlist_vector,
            weights
        )

        artist_recs_df = artist_recs_df.sort_values(by='similarity', ascending=False)
        artist_recs_df.to_csv('artist_recs.csv', index=False)

        # print("Time taken to get artist recommendations:", time.time() - start_time)
        print("<- re:get_artist_recs()")
        return artist_recs_df

    def track_vector(self, track):
        print('-> re:track_vector()')
        # One-hot encode categorical features
        track_vector = self.ohe_features(track)
        track_vector = track_vector.drop(columns=['artist', 'name', 'id'])
        print('<- re:track_vector()')
        return track_vector

    def recommend_by_track(self, rec_dataset, track_vector, track_id, user_top_tracks, class_items, recommended_ids=[]):
        print('-> re:recommend_by_track()')
        
        # Get track genre and drop release date
        track_genre_column = track_vector.columns[(track_vector.columns.str.startswith('track_genre_')) & (track_vector.iloc[0] == 1)].tolist()
        if track_genre_column:
            track_genre = track_genre_column[0].replace('track_genre_', '')
            print(track_genre)
        if 'release_date' in track_vector.columns:
            track_vector = track_vector.drop(columns=['release_date'])

        # Prepare data for recommendation
        track_vector, rec_dataset, ohe_rec_dataset  = self.prepare_data(self.sp, rec_dataset, track_vector, track_id, recommended_ids)

        # Apply weight to track genre
        weights = {track_genre: 0.9, 'default': 0.8}
        ohe_rec_dataset = self.apply_weights(ohe_rec_dataset, weights)

        # Get personalized track vector based on top tracks
        personalized_vector = self.get_personalized_vector(track_vector, weights, user_top_tracks, class_items)
        combined_vector = 0.9 * track_vector + 0.1 * personalized_vector
        
        # Calculate cosine similarity between final track vector and recommendations
        rec_dataset = self.calc_cosine_similarity(rec_dataset, ohe_rec_dataset, combined_vector, weights)
        top_songs = pd.DataFrame()
        
        genre_songs = rec_dataset[rec_dataset['track_genre'] == track_genre]
        top_songs = pd.concat([genre_songs.nlargest(45, 'similarity')])
        
        # Finalize and update the recommended songs
        recommendations = self.finalize_update_recommendations(top_songs, 'track')
        
        return recommendations

    # Helper Functions
    def ohe_features(self, df):
        print('-> re:ohe_features()')
        # start_time = time.time() 

        all_genres = pd.read_csv('../data/datasets/genre_counts.csv')
        df = pd.get_dummies(df, columns=['track_genre', 'mode', 'key'])  # One-hot encode the genre column
    
        ohe_columns = [col for col in df.columns if 'track_genre' in col or 'mode' in col or 'key' in col]
        df[ohe_columns] = df[ohe_columns].astype(int) 

        expected_genres = {'track_genre_' + genre for genre in all_genres['track_genre']}
        missing_genres = expected_genres - set(df.columns)
        for genre in missing_genres:
            df[genre] = 0

        expected_keys_modes = {f'key_{i}' for i in range(12)} | {f'mode_{i}' for i in range(2)}
        missing_keys_modes = expected_keys_modes - set(df.columns)
        for key_mode in missing_keys_modes:
            df[key_mode] = 0
        
        # print("Time taken to OHE Features:", time.time() - start_time, "s")
        print("<- re:ohe_features()")
        return df

    def normalize_vector(self, vector):
        num_tracks = len(vector)
        sum_vector = vector.sum(axis=0)
        print("len vector", num_tracks)
        normal_vector = sum_vector / num_tracks
        return normal_vector
        
    def get_top_genres(self, final_playlist_vector):
        print('-> re:get_top_genres()')
        # Get the genre columns from the final playlist vector
        genre_columns = final_playlist_vector.columns[final_playlist_vector.columns.str.startswith('track_genre_')]
        
        # Get the top 3 genres from the final playlist vector
        top_genres = final_playlist_vector[genre_columns].iloc[0].nlargest(3)
        top_genres_names = list(top_genres.index.str.replace('track_genre_', ''))
        total_genres_sum = final_playlist_vector[genre_columns].iloc[0].sum()

        top_genres_ratios = {genre_name: top_genres[f'track_genre_{genre_name}'] / total_genres_sum for genre_name in top_genres_names}

        # for genre, ratio in top_genres_ratios.items():
        #     print(f"{genre}: {ratio:.2%}")
        # print(top_genres_ratios)
    
        print("<- re:get_top_genres()")
        return top_genres_names, top_genres_ratios

    def prepare_data(self, sp, rec_dataset, vector, ids, recommended_ids, top_artist_names=None):
        print('-> re:prepare_data()')
        start_time = time.time()

        ohe_rec_dataset = self.ohe_features(rec_dataset)  # Save instance in SQL

        if top_artist_names is not None:
            top_artist_tracks = rec_dataset[rec_dataset['artists'].isin(top_artist_names)]
            ohe_top_artist_tracks = ohe_rec_dataset[ohe_rec_dataset['track_id'].isin(top_artist_tracks['track_id'])]

        # Exclude tracks from the ohe_rec_dataset that are already in the playlist track ids
        ohe_rec_dataset = ohe_rec_dataset[~ohe_rec_dataset['track_id'].apply(lambda x: x in ids or x in recommended_ids)]

        # Match ohe_rec_dataset and rec_dataset track ids
        rec_dataset = rec_dataset.merge(ohe_rec_dataset[['track_id']], on='track_id')
        
        # Sort the columns of the final vector and final recommendation dataframe to have the same order
        vector, ohe_rec_dataset = self.sort_columns(vector, ohe_rec_dataset)

        if top_artist_names is not None:
            ohe_top_artist_tracks = ohe_top_artist_tracks.reindex(columns=ohe_rec_dataset.columns)
        
        # Drop unnecessary columns from the vector and ohe_rec_dataset
        columns_to_drop = ['duration_ms', 'popularity'] # Reconsider if you should drop popularity
        vector.drop(columns=[col for col in columns_to_drop if col in vector.columns], axis=1, inplace=True)
        ohe_rec_dataset.drop(columns=[col for col in columns_to_drop if col in ohe_rec_dataset.columns], axis=1, inplace=True)
        
        if top_artist_names is not None:
            ohe_top_artist_tracks.drop(columns=[col for col in columns_to_drop if col in ohe_top_artist_tracks.columns], axis=1, inplace=True)
       
        # Replace any NaN values in the final vector or dataframe with 0
        vector.fillna(0, inplace=True,)
        ohe_rec_dataset.fillna(0, inplace=True)
        
        if top_artist_names is not None:
            ohe_top_artist_tracks.fillna(0, inplace=True)
        
        print("Time taken to prepare data:", time.time() - start_time, "s")
        print("<- re:prepare_data()")
        if top_artist_names is not None:
            return vector, rec_dataset, ohe_rec_dataset, top_artist_tracks, ohe_top_artist_tracks

        return vector, rec_dataset, ohe_rec_dataset

    def apply_weights(self, ohe_dataset, weights):
        # print('-> re:apply_weights()')
        # start_time = time.time()    

        for genre in ohe_dataset.columns:
            if genre.startswith('track_genre_'):
                stripped_genre = genre.replace('track_genre_', '')
                if stripped_genre in weights:
                    ohe_dataset[genre] *= weights[stripped_genre]
                else:
                    ohe_dataset[genre] *= weights['default']

        # print("Time taken to apply weights:", time.time() - start_time, "s")
        # print("<- re:apply_weights()")
        return ohe_dataset

    def calc_cosine_similarity(self, dataset, ohe_dataset, vector, weights):
        """
        Args:
            dataset (pandas.DataFrame): dataset to apply similarity to. // Can be rec_dataset, related_artist_tracks, or top_artist_tracks
            ohe_dataset (pandas.DataFrame): The one-hot encoded dataset.
            vector (numpy.ndarray): The vector being compared to the data.
            weights (dict): The weights for each track genre.
        Returns:
            pandas.DataFrame: The dataset with an additional column 'similarity' representing the cosine similarity.
        """
        print('-> re:calc_cosine_similarity()')
        # start_time = time.time()

        # Calculate the cosine similarity between the final vector and the final recommendation dataframe
        dataset['similarity'] = cosine_similarity(ohe_dataset.values, vector.values.reshape(1, -1))[:,0]
        
        nan_weight = weights.get('default', 0)

        weights = dataset['track_genre'].map(weights).fillna(nan_weight)
        dataset['similarity'] *= weights

        # print("cosine_similarity time:", time.time() - start_time, "seconds")
        print("<- re:calc_cosine_similarity()")
        return dataset

    def finalize_update_recommendations(self, top_songs, type, artist_recs=[], top_ratios={}):
        print('-> re:finalize_update_recommendations()')
        start_time = time.time()

        # Remove duplicates from top_songs
        top_songs = top_songs.drop_duplicates(subset=['track_name', 'artists'], keep='first')     

        # If artist_recs is not empty, remove duplicates from artist_recs
        if not isinstance(artist_recs, list):      
            artist_recs = artist_recs.drop_duplicates(subset=['track_name', 'artists'], keep='first')
            artist_recs = artist_recs[~artist_recs['track_id'].isin(top_songs['track_id'])]
        
        # Create a dataframe to store the recommended songs
        recommended_songs = pd.DataFrame(columns=top_songs.columns)

        if type == 'track':
            recommended_songs = top_songs.sample(15) # Randomly select 15 songs from the top 45
        elif type == 'playlist':
            total_songs = 30 # Final recommendation list size
            artist_rec_interval = 5 # Show once per 5 songs

            # Calculate genre proportions based on top genre ratios
            total_ratio = sum(top_ratios.values()) 

            # Calculates the normalized proportions of each genre relative to the total ratio
            # Finds how many recommendations of each genre would be needed to match the proportions
            proportions = {genre: ratio / total_ratio for genre, ratio in top_ratios.items()}
            genre_counts = {genre: int(total_songs * proportion) for genre, proportion in proportions.items()}
            print(genre_counts)
            remaining_songs = total_songs - sum(genre_counts.values())  # Calculate the number of remaining songs to recommended
            
            # Select songs based on genre counts
            for genre in genre_counts:
                genre_songs = top_songs[top_songs['track_genre'] == genre].head(genre_counts[genre])
                recommended_songs = pd.concat([recommended_songs, genre_songs], ignore_index=True)
            if remaining_songs > 0:
                # Filter the top songs to select only the songs that have not been already selected in recommended_songs
                remaining_songs_df = top_songs[~top_songs['track_id'].isin(recommended_songs['track_id'])].head(remaining_songs)
                recommended_songs = pd.concat([recommended_songs, remaining_songs_df], ignore_index=True)
            
            unique_artists = artist_recs['artists'].unique() # All unique artists in artist_recs
            used_artists = set() # Set to keep track of artists that have already been recommended
            artist_index = 0 # Start with first artist in artist_recs

            # Iterate through the recommended songs to insert artist recs at defined interval (5)
            for i in range(artist_rec_interval - 1, len(recommended_songs), artist_rec_interval):   
                # Initial check to see if all unique artists have already been recommended
                if artist_index >= len(unique_artists):
                    artist_index = 0
                    used_artists.clear()    
                # Find next unique, unused artist, if all unique artists have already been recommended, start over
                while unique_artists[artist_index] in used_artists and artist_index < len(unique_artists):
                    artist_index += 1
                    if artist_index >= len(unique_artists):
                        artist_index = 0
                        used_artists.clear()
                
                artist = unique_artists[artist_index] # Use next unique, unused artist
                used_artists.add(artist) # Mark artist as used
                genre = recommended_songs.iloc[i]['track_genre'] # Get genre of song at insertion index

                # TODO: prioritize the genre rec over the unused artist
               
                # Find recommendations from artist_recs that match the unique artist and genre of the song it will replace
                artist_genre_recs = artist_recs[(artist_recs['artists'] == artist) & (artist_recs['track_genre'] == genre)]
                
                # If not recommendations match both genre and artist, get most similar song by current artist
                if artist_genre_recs.empty:
                    artist_genre_recs = artist_recs[artist_recs['artists'] == artist].head(1)
                
                # If there is a match, remove from artist_recs and insert into recommended_songs
                if not artist_genre_recs.empty:
                    selected_song = artist_genre_recs.iloc[0] # Get first match
                    artist_recs = artist_recs[artist_recs['track_id'] != selected_song['track_id']] # Remove selected song from artist_recs
                    recommended_songs = pd.concat([recommended_songs.iloc[:i], artist_genre_recs.iloc[:1], recommended_songs.iloc[i + 1:]], ignore_index=True) # Insert
                
                # If there is not match for either genre or artist, keep the original song in the recommended_songs
                
                artist_index += 1 # Move to next unique, unused artist

        recommended_ids = recommended_songs['track_id'].tolist()
        recommended_songs.to_csv('recommended_songs.csv')
        
        print("Finalized recommendations... :", time.time() - start_time, "s")
        print('<- re:finalize_update_recommendations()')
        return recommended_ids

    def sort_columns(self, vector, ohe_dataset):
        # Print none columns:
        print(vector.columns[vector.isnull().any()])
        common_cols = vector.columns.intersection(ohe_dataset.columns)
        vector = vector[common_cols]
        ohe_dataset = ohe_dataset[common_cols]
        return vector, ohe_dataset

    def clean_recommendations(self, df):
        df['similarity'] = (df['similarity'] * 100).round().astype(int).astype(str) + '% similar'
        df = df[['track_name', 'artists', 'track_genre', 'similarity', 'Link', 'track_id']]
        df = df.rename(columns={'track_name': 'Song', 'artists': 'Artist', 'track_genre': 'Genre', 'similarity': 'Similarity', 'Link': 'Link', 'track_id': 'ID'})
        df = df.reset_index(drop=True)  # Reset the index + 1 
        df.index = df.index + 1 
        return df

    def get_user_top_tracks(self):
        print('-> re:get_user_top_tracks()')    
        start_time = time.time()

        user_top_tracks = self.sql_cnx.get_user_top_tracks(self.unique_id)
       
        short_term_track_ids = [None] * 20
        medium_term_track_ids = [None] * 20
        long_term_track_ids = [None] * 20

        # Insert track IDs at their rank index
        for track in user_top_tracks:
            if track['short_term_rank'] is not None:
                short_term_track_ids[track['short_term_rank'] - 1] = track['track_id']
            if track['medium_term_rank'] is not None:
                medium_term_track_ids[track['medium_term_rank'] - 1] = track['track_id']
            if track['long_term_rank'] is not None:
                long_term_track_ids[track['long_term_rank'] - 1] = track['track_id']

        print("Getting user top tracks... :", time.time() - start_time, "s")
        print('<- re:get_user_top_tracks()')
        return short_term_track_ids

    def get_user_top_artists(self): 
        print('-> re:get_user_top_artists()')
        start_time = time.time()

        user_top_artists = self.sql_cnx.get_user_top_artists(self.unique_id)
        short_term_artists = sorted([item for item in user_top_artists if item['short_term_rank'] is not None], key=lambda x: x['short_term_rank'])
  
        for artist in user_top_artists:
            artist.pop('id', None)
            artist.pop("unique_id", None)
       
        print("Getting user top artists (short term)... :", time.time() - start_time, "s")
        print('<- re:get_user_top_artists()')
        return short_term_artists 
    
    def get_personalized_vector(self, vector, weights, user_top_tracks, class_items):
        print("-> re:get_personalized_vector()")
        start_time = time.time()

        user_top_tracks = self.sp.predict(user_top_tracks, 'playlist', class_items) # list items
        ohe_user_top_tracks = self.ohe_features(user_top_tracks)

        ohe_user_top_tracks, vector = self.sort_columns(ohe_user_top_tracks, vector)

        # Calculate the weighted similarity of user top tracks against the vector
        user_top_tracks['similarity'] = cosine_similarity(ohe_user_top_tracks.values, vector.values.reshape(1, -1))[:,0]
        # Map genre weights to user top tracks
        nan_weight = weights.get('default') 
        genre_weights = user_top_tracks['track_genre'].map(weights).fillna(nan_weight) 
        # Apply genre weights for weighted similarity
        user_top_tracks['weighted_similarity'] = user_top_tracks['similarity'] * genre_weights

        # Normalize the final playlist vector
        personalized_vector = ohe_user_top_tracks.multiply(user_top_tracks['weighted_similarity'], axis=0).sum() / user_top_tracks['weighted_similarity'].sum()
        personalized_vector = personalized_vector.to_frame().T

        print("Getting personalized vector... :", time.time() - start_time, "s")
        print("<- re:get_personalized_vector()")   
        return personalized_vector


    def get_user_recently_played(self):
        print("-> re:get_user_recently_played()")
        start_time = time.time()

        recently_played = self.sql_cnx.get_user_recently_played(self.unique_id)
        for item in recently_played:
            item.pop('id', None)
            item.pop("unique_id", None)
        
        print("Getting user recently played... :", time.time() - start_time, "s")
        print("<- re:get_user_recently_played()")
        return recently_played
    
    def get_related_artists(self, top_artist_ids, top_artists_names, user_top_artists):
        print("-> re:get_related_artists()")
        start_time = time.time()

        # Create a dictionary mapping artist IDs to names
        artist_id_to_name = {artist['artist_id']: artist['artist_name'] for artist in user_top_artists}
        related_artists = {}

        # Get related artists for each top artist
        for artist_id in top_artist_ids:
            data = self.sp.sp.artist_related_artists(artist_id)['artists']
            artist_name = artist_id_to_name.get(artist_id, artist_id)  # Use artist_id as fallback if name not found
            related_artists[artist_name] = {artist['id']: artist['name'] for artist in data} # Map related artist IDs to their names in related_artists
        
        top_artist_names = set() # To store unique artist names

        for main_artist, related_artist in related_artists.items():
            top_artist_names.add(main_artist) # Add main artist name to the set
            top_artist_names.update(related_artist.values()) # Add the main artist's related artists to the set

        top_artist_names = list(top_artist_names)

        random_artists = random.sample(top_artist_names, min(6, len(top_artist_names)))

        print("Time taken to get related artists:", time.time() - start_time, "s")
        print("<- re:get_related_artists()")    
        return random_artists
       
    def find_similar_artists(self, top_artist_tracks, ohe_top_artist_tracks, playlist_vector, top_genres, top_ratios, weights):
        print("-> re:find_similar_artists()")
        # start_time = time.time()
        
        ohe_top_artist_tracks = self.apply_weights(ohe_top_artist_tracks, weights)

        # Calculate cosine similarity between final playlist vector and recommendations
        similar_artists_df = self.calc_cosine_similarity(top_artist_tracks, ohe_top_artist_tracks, playlist_vector, weights)

        similar_artists_df = similar_artists_df.sort_values(by='similarity', ascending=False)
        
        # Group by artists and track genre to find how many entries in each genre each artist has
        artist_genre_counts = similar_artists_df.groupby(['artists', 'track_genre']).size().unstack(fill_value=0)
        
        # Fill in missing genres with 0
        for genre in top_genres:
            if genre not in artist_genre_counts.columns:
                artist_genre_counts[genre] = 0

        # Calculate the ratio of each genre for each artist for their catalog
        artist_genre_ratios = artist_genre_counts.div(artist_genre_counts.sum(axis=1), axis=0)
        # Convert the top genre ratios to a Series, making sure the order is correct
        top_ratios = pd.Series(top_ratios, index=top_genres)
        
        # Calculate the weighted similarities for each artist by multiplying the artist's genre ratios by the top genre ratios
        weighted_similarities = artist_genre_ratios[top_genres].multiply(top_ratios, axis=1).sum(axis=1)

        # Add the weighted similarities to the original similarities to get the final similarity
        similar_artists_df = similar_artists_df.set_index('artists')
        similar_artists_df['weighted_similarity'] = weighted_similarities
        similar_artists_df['final_similarity'] = similar_artists_df['similarity'] + similar_artists_df['weighted_similarity']

        # Get the mean similarity for each artist
        mean_similarities = similar_artists_df.groupby('artists')['final_similarity'].mean()

        # Get the top 3 artists based on the mean similarity
        top_artists = mean_similarities.nlargest(3).reset_index()
        
        top_artists_dict = {artist['artists']: artist['final_similarity'] for _, artist in top_artists.iterrows() } # if artist['final_similarity'] > weights[top_genres[1]]

        # print("Time taken to find similar artists:", time.time() - start_time, "s")
        print("<- re:find_similar_artists()")  
        return top_artists_dict
        
    def create_weights(self, top_genres, top_ratios):
        # print('-> re:create_weights()')
        # start_time = time.time()

        weights = {genre: ratio for genre, ratio in top_ratios.items()}

        min_top_genre_weight = min(weights.values())
        default_weight = min_top_genre_weight * 0.8 # Lower than smallest top genre weight

        weights['default'] = default_weight 

        print(weights)
        
        # print("Time taken to create weights:", time.time() - start_time, "s")
        # print('<- re:create_weights()')
        return weights


        
