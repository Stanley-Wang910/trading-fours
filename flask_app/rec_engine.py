import pandas as pd
import time
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
from spotify_client import SpotifyClient

import random


class RecEngine:
    def __init__(self, spotify_client, unique_id, sql_cnx, previously_recommended=None):
        self.sp = spotify_client
        self.unique_id = unique_id
        self.sql_cnx = sql_cnx
        self.recommended_songs = set(previously_recommended) if previously_recommended else set()
              
        self.weights = {0: 0.9, 1: 0.85, 2: 0.80} # Default weights for the top 3 genres, easy to calibrate

    def playlist_vector(self, playlist_df, weight=1.1):
        """
        Calculates the playlist vector based on the given playlist and recommendation dataframes.

        Args:
            playlist_df (pandas.DataFrame): The dataframe representing the playlist.
            rec_df (pandas.DataFrame): The dataframe representing the recommendations.
            weight (float, optional): The weight factor for the months behind. Defaults to 1.1.

        Returns:
            pandas.Series: The final playlist vector.
        """
        playlist_df = self.ohe_features(playlist_df)

        # Drop unnecessary columns from the playlist dataframe
        playlist_df = playlist_df.drop(columns=['artist', 'name', 'id'])

        # Calculate the most recent date in the playlist
        most_recent_date = playlist_df.iloc[0, 0]
        most_recent_date = pd.to_datetime(most_recent_date, unit='ms').tz_localize(None)

        if most_recent_date != pd.Timestamp('1970-01-01 00:00:00') or most_recent_date != 0:
            # Calculate the number of months behind for each track in the playlist
            playlist_df['date_added'] = pd.to_datetime(playlist_df['date_added'], unit='ms').dt.tz_localize(None)
            playlist_df['months_behind'] = ((most_recent_date - playlist_df['date_added']).dt.days / 30).astype(int)

            # Calculate the weight for each track based on the months behind
            playlist_df['weight'] = weight ** (-playlist_df['months_behind'])
            playlist_df_weighted = playlist_df.copy()

            # Update the values in the playlist dataframe with the weighted values
            cols_to_update = playlist_df_weighted.columns.difference(['date_added', 'weight', 'months_behind'])
            playlist_df_weighted.update(playlist_df_weighted[cols_to_update].mul(playlist_df_weighted.weight, axis=0))

            # Get the final playlist vector by excluding unnecessary columns
            final_playlist_vector = playlist_df_weighted[playlist_df_weighted.columns.difference(['date_added', 'weight', 'months_behind'])]
        else:
            # If the most recent date is the default value, exclude only the 'date_added' column
            final_playlist_vector = playlist_df[playlist_df.columns.difference(['date_added'])]

        # Sum the values along the rows to get a single vector
        final_playlist_vector = final_playlist_vector.sum(axis=0)

        # Normalize the final playlist vector
        final_playlist_vector = self.normalize_vector(final_playlist_vector)

        # Transposes into a one row vector
        final_playlist_vector = final_playlist_vector.to_frame().T

        return final_playlist_vector

    def recommend_by_playlist(self, rec_dataset, final_playlist_vector, playlist_id, class_items):
        
        top_genres = self.get_top_genres(final_playlist_vector)
        
        # Prepare data for recommendation
        final_playlist_vector, final_rec_df, recommendations_df = self.prepare_data(self.sp, top_genres, rec_dataset, final_playlist_vector, playlist_id, 'playlist')
        personalized_vector = self.similar_top_tracks(final_playlist_vector, top_genres, class_items)
       

        
        # Apply weights to the top genres
        self.weights = {top_genres[0]: 0.9, top_genres[1]: 0.85, top_genres[2]: 0.8}
        final_rec_df = self.apply_weights(final_rec_df, self.weights)

        # Calculate cosine similarity between final playlist vector and recommendations

        combined_vector = 0.7 * final_playlist_vector + 0.3 * personalized_vector
        recommendations_df = self.calc_cosine_similarity(final_rec_df, combined_vector, recommendations_df, self.weights, 'playlist')

        

        # Initialize an empty DataFrame to store top songs
        top_songs = pd.DataFrame()

        # Select top songs from each genre based on similarity and add them to the top_songs DataFrame
        for genre in top_genres:
            genre_songs = recommendations_df[recommendations_df['track_genre'] == genre]
            top_songs = pd.concat([top_songs, genre_songs.nlargest(90 // len(top_genres), 'similarity')])

        # Finalize and update the recommended songs
        top_recommendations_df = self.finalize_update_recommendations(top_songs, self.recommended_songs, 'playlist')

        return top_recommendations_df

    def track_vector(self, track):
        # One-hot encode categorical features
        track_vector = self.ohe_features(track)
        track_vector = track_vector.drop(columns=['artist', 'name', 'id'])

        return track_vector

    def recommend_by_track(self, rec_dataset, track_vector, track_id, class_items):
        """
        Recommends songs based on a given track.

        Args:
            rec_dataset (DataFrame): The recommendation dataset.
            track_vector (DataFrame): The vector representation of the track.
            final_rec_df (DataFrame): The final recommendation dataframe.
            era_choice (str): Indicates whether to consider the era of the track.

        Returns:
            DataFrame: The top recommended songs based on the given track.
        """
        # Get track genre
        track_genre_column = track_vector.columns[(track_vector.columns.str.startswith('track_genre_')) & (track_vector.iloc[0] == 1)].tolist()
        if track_genre_column:
            track_genre = track_genre_column[0].replace('track_genre_', '')
        print(track_genre)
      
        if 'release_date' in track_vector.columns:
            track_vector = track_vector.drop(columns=['release_date'])

        # Prepare data for recommendation
        final_track_vector, final_rec_df, recommendations_df = self.prepare_data(self.sp, [track_genre], rec_dataset, track_vector, track_id)
        personalized_vector = self.similar_top_tracks(final_track_vector, [track_genre], class_items)
        
        # Apply weight to track genre
        weight = {track_genre: 0.9}
        final_rec_df = self.apply_weights(final_rec_df, weight)

        combined_vector = 0.7 * final_track_vector + 0.3 * personalized_vector
        # Calculate cosine similarity between final track vector and recommendations
        recommendations_df = self.calc_cosine_similarity(final_rec_df, combined_vector, recommendations_df, weight, 'track')

        # Initialize an empty DataFrame to store top songs
        top_songs = pd.DataFrame()
        
        # Get top songs based on similarity
        top_songs = pd.concat([recommendations_df.nlargest(45, 'similarity')])
        
        # Finalize and update the recommended songs
        top_recommendations_df = self.finalize_update_recommendations(top_songs, self.recommended_songs, 'track')
        return top_recommendations_df

    # Helper Functions
    def ohe_features(self, df):
        all_genres = pd.read_csv('data/datasets/genre_counts.csv')
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
            
        return df

    def normalize_vector(self, vector):
        num_tracks = len(vector)
        normal_vector = vector / num_tracks
        return normal_vector

    def get_top_genres(self, final_playlist_vector):
        # Get the genre columns from the final playlist vector
        genre_columns = final_playlist_vector.columns[final_playlist_vector.columns.str.startswith('track_genre_')]
        
        # Get the top 3 genres from the final playlist vector
        top_genres = final_playlist_vector[genre_columns].iloc[0].nlargest(3).index.str.replace('track_genre_', '')
        print(top_genres)
        return top_genres

    def prepare_data(self, sp, top_genres, rec_dataset, vector, id, type='track'):
        # Correct handling for recommendation type
        if type == 'playlist':
            ids = self.sp.analyze_playlist(id, 'rec') # Why?
        else:
            ids = id # Handle for track recommendation
        # One-hot encode the genre column in both dataframes
        # final_rec_df = rec_dataset[rec_dataset['track_genre'].isin(top_genres)]

        final_rec_df = self.ohe_features(rec_dataset) ### Save instance in SQL
        print("final_rec_df length:", len(final_rec_df))
        
        # Exclude tracks from the recommendation dataframe that are already in the playlist
        final_rec_df = final_rec_df[~final_rec_df['track_id'].isin(ids)] ###

        # Filter the recommendations dataframe based on the track ids in the final recommendation dataframe
        rec_dataset = rec_dataset.merge(final_rec_df[['track_id']], on='track_id')
        
        # Exclude songs that have already been recommended
        rec_dataset = rec_dataset[~rec_dataset['track_id'].isin(self.recommended_songs)]
        final_rec_df = final_rec_df.merge(rec_dataset[['track_id']], on='track_id')
        
        # Sort the columns of the final vector and final recommendation dataframe to have the same order
        final_vector, final_rec_df = self.sort_columns(vector, final_rec_df)

        # Drop unnecessary columns from the final playlist vector and final recommendation dataframe
        final_vector.drop(['duration_ms', 'popularity'], axis=1, inplace=True)    ####
        final_rec_df.drop(['duration_ms', 'popularity'], axis=1, inplace=True)   

        # Replace any NaN values in the final vector or dataframe with 0
        final_vector.fillna(0, inplace=True)
        final_rec_df.fillna(0, inplace=True)

        return final_vector, final_rec_df, rec_dataset

    def apply_weights(self, final_rec_df, weights):
        for genre in final_rec_df.columns:
            if genre.startswith('track_genre_'):
                stripped_genre = genre.replace('track_genre_', '')
                if stripped_genre in weights:
                    final_rec_df[genre] *= weights[stripped_genre]
        return final_rec_df

    def calc_cosine_similarity(self, final_rec_df, combined_vector, recommendations_df, weights, rec_type):
        
        # Calculate the cosine similarity between the final vector and the final recommendation dataframe
        recommendations_df['similarity'] = cosine_similarity(final_rec_df.values, combined_vector.values.reshape(1, -1))[:,0]
        
        if rec_type == 'playlist':
            nan_weight = 0.75 # For tracks that aren't in the top 3 genres
        elif rec_type == 'track':
            nan_weight = 0.85

        weights = recommendations_df['track_genre'].map(weights).fillna(nan_weight)
        recommendations_df['similarity'] *= weights
        return recommendations_df

    def finalize_update_recommendations(self, top_songs, recommended_songs, type):

        top_songs = top_songs.drop_duplicates(subset=['track_name', 'artists'], keep='first')
        
        # top_recommendations_df = top_songs.sort_values(by='similarity', ascending=False)
        
        selected_songs = pd.DataFrame(columns=top_songs.columns)

        if type == 'track':
            selected_songs = top_songs.sample(15)
        elif type == 'playlist':

            genre_counts = top_songs['track_genre'].value_counts().head(3) # Make more precise

            total_songs = 30
            genre1_count = int(total_songs * 0.6) # Most Occurences
            genre2_count = int(total_songs * 0.25)
            genre3_count = total_songs - genre1_count - genre2_count

            genre1_songs = top_songs[top_songs['track_genre'] == genre_counts.index[0]].nlargest(genre1_count, 'similarity')
            genre2_songs = top_songs[top_songs['track_genre'] == genre_counts.index[1]].nlargest(genre2_count, 'similarity')
            genre3_songs = top_songs[top_songs['track_genre'] == genre_counts.index[2]].nlargest(genre3_count, 'similarity')

            selected_songs = pd.concat([genre3_songs, genre2_songs, genre1_songs])
            selected_songs = selected_songs.sample(frac=1).reset_index(drop=True)
        
        recommended_ids = selected_songs['track_id'].tolist()
        
        print(selected_songs)

        return recommended_ids

    def sort_columns(self, plt_vector, final_df):
        common_cols = plt_vector.columns.intersection(final_df.columns)
        plt_vector = plt_vector[common_cols]
        final_df = final_df[common_cols]
        return plt_vector, final_df

    def clean_recommendations(self, df):
        df['similarity'] = (df['similarity'] * 100).round().astype(int).astype(str) + '% similar'
        df = df[['track_name', 'artists', 'track_genre', 'similarity', 'Link', 'track_id']]
        df = df.rename(columns={'track_name': 'Song', 'artists': 'Artist', 'track_genre': 'Genre', 'similarity': 'Similarity', 'Link': 'Link', 'track_id': 'ID'})
        df = df.reset_index(drop=True)  # Reset the index + 1 
        df.index = df.index + 1 
        return df

    def get_user_top_tracks(self):
        top_tracks = self.sql_cnx.get_user_top_tracks(self.unique_id)
       
        short_term_track_ids = [None] * 20
        medium_term_track_ids = [None] * 20
        long_term_track_ids = [None] * 20

        # Insert track IDs at their rank index
        for track in top_tracks:
            if track['short_term_rank'] is not None:
                short_term_track_ids[track['short_term_rank'] - 1] = track['track_id']
            if track['medium_term_rank'] is not None:
                medium_term_track_ids[track['medium_term_rank'] - 1] = track['track_id']
            if track['long_term_rank'] is not None:
                long_term_track_ids[track['long_term_rank'] - 1] = track['track_id']

        return short_term_track_ids, medium_term_track_ids, long_term_track_ids
    
    def similar_top_tracks(self, final_vector, final_genres, class_items):
        short_term, medium_term, long_term = self.get_user_top_tracks()
        random.shuffle(short_term)
        sub_section_size = 5
        sub_sections = [short_term[i:i+sub_section_size] for i in range(0, len(short_term), sub_section_size)] # Genius List Comp
        max_similarity = -float('inf') #
        most_similar_sub_section = None
        best_final_vector = None
        best_similar_vector = None
        for sub_section in sub_sections: #
            sub_section_tracks = self.sp.predict(sub_section, 'playlist', class_items)
            sub_section_vector = self.playlist_vector(sub_section_tracks)
            sub_section_vector.drop(['duration_ms', 'popularity'], axis=1, inplace=True)
            sub_section_top_genres = self.get_top_genres(sub_section_vector)

            weights = {genre: 1.2 for genre in final_genres if genre in sub_section_top_genres}        
            weighted_sub_section_vector = self.apply_weights(sub_section_vector, weights)
            weighted_final_vector = self.apply_weights(final_vector, weights)

            similarity = cosine_similarity(weighted_final_vector.values.reshape(1, -1), weighted_sub_section_vector.values.reshape(1, -1))[0][0]

            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_sub_section = sub_section
                best_final_vector = weighted_final_vector
                best_similar_vector = sub_section_vector
                

        similar_names = self.sp.sp.tracks(most_similar_sub_section) #
        similar_names = [track['name'] for track in similar_names['tracks']] 
        print(f"Most similar tracks: {similar_names}")


        return best_similar_vector


    def get_user_top_artists(self): 
        top_artists = self.sql_cnx.get_user_top_artists(self.unique_id)
        short_term_artists = sorted([item for item in top_artists if item['short_term_rank'] is not None], key=lambda x: x['short_term_rank'])
        medium_term_artists = sorted([item for item in top_artists if item['medium_term_rank'] is not None], key=lambda x: x['medium_term_rank'])
        long_term_artists = sorted([item for item in top_artists if item['long_term_rank'] is not None], key=lambda x: x['long_term_rank'])
        
        # Remove 'id' key from each artist dictionary
        for artist in top_artists:
            artist.pop('id', None)
            artist.pop("unique_id", None)

        return short_term_artists, medium_term_artists, long_term_artists

    def get_user_recently_played(self):
        recently_played = self.sql_cnx.get_user_recently_played(self.unique_id)
        for item in recently_played:
            item.pop('id', None)
            item.pop("unique_id", None)
        
        return recently_played

        


       



        
