import pandas as pd
import time
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
from spotify_client import SpotifyClient


class RecEngine:
    def __init__(self, spotify_client, previously_recommended=None):
        self.sp = spotify_client
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

        if most_recent_date != pd.Timestamp('1970-01-01 00:00:00'):
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

    def recommend_by_playlist(self, rec_dataset, final_playlist_vector, playlist_ids):
        """
        Recommends songs based off the given playlist.

        Args:
            rec_dataset (DataFrame): DataFrame containing information about songs and their genres.
            final_playlist_vector (DataFrame): DataFrame representing the final playlist vector.
            final_rec_df (DataFrame): DataFrame representing the final recommendation dataframe.

        Returns:
            DataFrame: DataFrame containing the top recommended songs.
        """
        top_genres = self.get_top_genres(final_playlist_vector)

        # Prepare data for recommendation
        final_playlist_vector, final_rec_df, recommendations_df = self.prepare_data(rec_dataset, final_playlist_vector, playlist_ids)

        # Apply weights to the top genres
        self.weights = {top_genres[0]: 0.9, top_genres[1]: 0.85, top_genres[2]: 0.80}
        final_rec_df = self.apply_weights(final_rec_df, self.weights)

        # Calculate cosine similarity between final playlist vector and recommendations
        recommendations_df = self.calc_cosine_similarity(final_rec_df, final_playlist_vector, recommendations_df, self.weights, 'playlist')

        # Initialize an empty DataFrame to store top songs
        top_songs = pd.DataFrame()

        # Select top songs from each genre based on similarity and add them to the top_songs DataFrame
        for genre in top_genres:
            genre_songs = recommendations_df[recommendations_df['track_genre'] == genre]
            top_songs = pd.concat([top_songs, genre_songs.nlargest(21 // len(top_genres), 'similarity')])

        # Randomly select 7 songs from the top_songs DataFrame
        selected_songs = top_songs.sample(7)

        # Select top 30 songs that do not belong to the top genres based on similarity
        remaining_songs = recommendations_df[~recommendations_df['track_genre'].isin(top_genres)].nlargest(30, 'similarity')

        # Randomly select 3 songs from the remaining_songs DataFrame and add them to the selected_songs DataFrame
        selected_songs = pd.concat([selected_songs, remaining_songs.sample(3)])

        # Finalize and update the recommended songs
        top_recommendations_df, recommended_ids = self.finalize_update_recommendations(selected_songs, self.recommended_songs, 'playlist')

        return top_recommendations_df, recommended_ids

    def track_vector(self, track):
       
        # One-hot encode categorical features
        track_vector = self.ohe_features(track)
        track_vector = track_vector.drop(columns=['artist', 'name', 'id'])

        return track_vector

    def recommend_by_track(self, rec_dataset, track_vector, track_id, era_choice):
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
        # Get track release date
        track_release_date = track_vector['release_date'].values[0]
        track_release_date = datetime.strptime(track_release_date[:4], '%Y')
        
        # Drop release_date column from track_vector
        track_vector = track_vector.drop(columns=['release_date'])
        # Get track genre
        track_genre_column = track_vector.columns[(track_vector.columns.str.startswith('track_genre_')) & (track_vector.iloc[0] == 1)].tolist()
        if track_genre_column:
            track_genre = track_genre_column[0].replace('track_genre_', '')
        
        # Prepare data for recommendation
        final_track_vector, final_rec_df, recommendations_df = self.prepare_data(rec_dataset, track_vector, track_id)
        
        # Apply weight to track genre
        print(track_genre)
        weight = {track_genre: 0.9}
        final_rec_df = self.apply_weights(final_rec_df, weight)
        
        # Calculate cosine similarity between final track vector and recommendations
        recommendations_df = self.calc_cosine_similarity(final_rec_df, final_track_vector, recommendations_df, weight, 'track')
        
        # Initialize an empty DataFrame to store top songs
        top_songs = pd.DataFrame()
        
        # Get top songs based on similarity
        top_songs = pd.concat([recommendations_df.nlargest(150, 'similarity')])
        
        # Initialize selected_songs DataFrame
        selected_songs = pd.DataFrame(columns=top_songs.columns)
        
        if era_choice == 'yes':
            count = 0
            # Iterate over top songs
            for index, row in top_songs.iterrows():
                if count >= 15:
                    break
                track_id = row['track_id']
                release_date = self.sp.get_release_date(track_id) # Slow because it needs to make a request to the Spotify API for each track
                try:
                    release_date = datetime.strptime(release_date[:4], '%Y')  # Only take the first 4 characters (the year)
                except ValueError:
                    continue
                # Calculate the start and end dates of the 5-year period
                start_date = release_date - timedelta(days=5*365)
                end_date = release_date + timedelta(days=5*365)
                if start_date <= track_release_date <= end_date:
                    selected_songs.loc[len(selected_songs)] = row
                    count += 1
        else: 
            # Randomly select 5 songs from top songs
            selected_songs = top_songs.sample(15)
        
        # Finalize and update the recommended songs
        top_recommendations_df = self.finalize_update_recommendations(selected_songs, self.recommended_songs, 'track')
        
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
        return top_genres

    def prepare_data(self, rec_dataset, vector, ids):
        # One-hot encode the genre column in both dataframes
        final_rec_df = self.ohe_features(rec_dataset) ###
        
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

    def calc_cosine_similarity(self, final_rec_df, final_vector, recommendations_df, weights, rec_type):
        
        # Calculate the cosine similarity between the final vector and the final recommendation dataframe
        recommendations_df['similarity'] = cosine_similarity(final_rec_df.values, final_vector.values.reshape(1, -1))[:,0]
        if rec_type == 'playlist':
            nan_weight = 0.7
        elif rec_type == 'track':
            nan_weight = 0.85

        weights = recommendations_df['track_genre'].map(weights).fillna(nan_weight)
        recommendations_df['similarity'] *= weights
        return recommendations_df

    def finalize_update_recommendations(self, selected_songs, recommended_songs, rec_type):
        if rec_type == 'playlist':
            # Sort the selected songs based on similarity in descending order
            top_recommendations_df = selected_songs.sort_values(by='similarity', ascending=False)
        elif rec_type == 'track':
            if len(selected_songs) < 5:
                top_recommendations_df = selected_songs.sort_values(by='similarity', ascending=False)
            else:
                selected_songs = selected_songs.sample(5)
                top_recommendations_df = selected_songs.sort_values(by='similarity', ascending=False)

        # Set the display option to show the full text of each column
        pd.set_option('display.max_colwidth', None)

        top_recommendations_df['Link'] = 'https://open.spotify.com/track/' + top_recommendations_df['track_id']
        
        # Update the recommended_songs set with the track_ids of the top recommendations
        # self.recommended_songs.update(top_recommendations_df['track_id'].values)
        
        recommended_ids = top_recommendations_df['track_id'].tolist()


        # Clean the recommendations DataFrame by formatting the similarity column and selecting specific columns
        top_recommendations_df = self.clean_recommendations(top_recommendations_df)
        return top_recommendations_df, recommended_ids

    def sort_columns(self, plt_vector, final_df):
        common_cols = plt_vector.columns.intersection(final_df.columns)
        plt_vector = plt_vector[common_cols]
        final_df = final_df[common_cols]
        return plt_vector, final_df

    def clean_recommendations(self, df):
        df['similarity'] = (df['similarity'] * 100).round().astype(int).astype(str) + '% similar'
        df = df[['track_name', 'artists', 'track_genre', 'similarity', 'Link']]
        df = df.rename(columns={'track_name': 'Song', 'artists': 'Artist', 'track_genre': 'Genre', 'similarity': 'Similarity', 'Link': 'Link'})
        df = df.reset_index(drop=True)  # Reset the index + 1 
        df.index = df.index + 1 
        return df
        
   
    

    def print_loading_message(self):
        print("\nFinding recommendations", end="", flush=True)
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(0.25)
           