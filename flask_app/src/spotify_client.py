import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
import spotipy
import requests
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from spotipy.client import SpotifyException
import warnings
import random
import time

warnings.filterwarnings("ignore")



class SpotifyClient:
    def __init__(self, sp):

        self.sp = sp

    # def __init__(self, client_id, client_secret, redirect_uri, user_id, scope):
    #     self.client_id = client_id
    #     self.client_secret = client_secret
    #     self.redirect_uri = redirect_uri
    #     self.user_id = user_id
    #     self.scope = scope

    #     auth_manager = SpotifyOAuth(client_id=self.client_id,
    #                                 client_secret=self.client_secret,
    #                                 redirect_uri=self.redirect_uri,
    #                                 scope=self.scope,
    #                                 username=self.user_id)
    #     self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def get_user_saved_info(self):
        user_profile = self.sp.current_user()

        all_playlists = []

        user_playlists = self.sp.current_user_playlists() 

        while user_playlists:
            all_playlists.extend(user_playlists['items'])
            if user_playlists['next']:
                user_playlists = self.sp.next(user_playlists)
            else:
                user_playlists = None

        recently_played = self.sp.current_user_recently_played()
        top_artists_short = self.sp.current_user_top_artists(20,0, 'short_term')
        top_artists_med = self.sp.current_user_top_artists(20,0, 'medium_term')
        top_artists_long = self.sp.current_user_top_artists(20,0, 'long_term')
        top_artists = {
            'short_term': top_artists_short,
            'medium_term': top_artists_med,
            'long_term': top_artists_long
        }
        top_tracks_short = self.sp.current_user_top_tracks(20,0, 'short_term')
        top_tracks_med = self.sp.current_user_top_tracks(20,0, 'medium_term')
        top_tracks_long = self.sp.current_user_top_tracks(20,0, 'long_term')
        top_tracks = {
            'short_term': top_tracks_short,
            'medium_term': top_tracks_med,
            'long_term': top_tracks_long
        }
        return user_profile, all_playlists, recently_played, top_artists, top_tracks
    
    
    def analyze_my_playlist(self, playlist_name, id_dic, sp):
        playlist_id = id_dic[playlist_name]
        self.analyze_playlist(playlist_id)

    def playlist_base_features(self, playlist):
        playlist_features = {
            'playlist_image': playlist['images'][0]['url'],   
            'playlist_owner': playlist['owner']['display_name'],
            'playlist_owner_link' : playlist['owner']['external_urls']['spotify'],
            'playlist_name' : playlist['name']
        }
        return playlist_features


    def analyze_playlist(self, input_data, type_analyze='classify'):
        """
        Analyzes a Spotify playlist by retrieving the tracks, their audio features, and merging them into a DataFrame.

        Parameters:
        - playlist_id (str): The ID of the Spotify playlist to analyze.

        Returns:
        - playlist_with_features (pd.DataFrame): A DataFrame containing the playlist tracks and their audio features.
        """
        print("-> sp:analyze_playlist()")
        if isinstance(input_data, dict):
            start_time = time.time()
            # Input is a playlist ID
            playlist_id = input_data
            
            # Retrieve the tracks from the playlist
            playlist = input_data
            playlist_data = []
            playlist_tracks = playlist['tracks']

            while playlist_tracks:
                playlist_data.extend([
                    {
                        'artist': track_item['track']['artists'][0]['name'],
                        'name': track_item['track']['name'],
                        'id': track_item['track']['id'],
                        'date_added': track_item['added_at'],
                        'popularity': track_item['track']['popularity'],
                        'explicit': track_item['track']['explicit']
                    }
                    for track_item in playlist_tracks['items']
                    if track_item['track'] and track_item['track']['id'] and track_item['track']['type'] == 'track'
                ])
                if playlist_tracks['next']:
                    playlist_tracks = self.sp.next(playlist_tracks)
                else:
                    playlist_tracks = None

            # Create a DataFrame from the playlist data
            playlist = pd.DataFrame(playlist_data)
            playlist['date_added'] = pd.to_datetime(playlist['date_added'])
            playlist = playlist.sort_values('date_added', ascending=False)
            playlist = playlist.drop_duplicates(subset='id')

            # Retrieve the track IDs from the playlist
            track_ids = playlist['id'].tolist()
            print("Playlist tracks received and organized in {:.2f} seconds.".format(time.time() - start_time))
            
        elif isinstance(input_data, list):
            # Input is a list of track IDs
            track_ids = input_data
            
            # Retrieve track information for the given track IDs
            tracks_info = self.sp.tracks(track_ids)['tracks']
            
            # Create a DataFrame from the track information
            playlist = pd.DataFrame([{
                'artist': track['artists'][0]['name'],
                'name': track['name'],
                'id': track['id'],
                'popularity': track['popularity'],
                'explicit': track['explicit']
            } for track in tracks_info])
        
        else:
            raise ValueError("Invalid input type. Expected a playlist ID or a list of track IDs.")
        
        if type_analyze == 'rec':
            return track_ids
        
        # Handle Pagination
        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]
        
        audio_features_list = []
        for chunk in chunks(track_ids, 100):
            audio_features_list.extend(self.sp.audio_features(chunk))

        # Filter out None entries 
        audio_features_list = [features for features in audio_features_list if features is not None]


        audio_features_df = pd.DataFrame(audio_features_list) # Consider filling none with 0

        # Select specific columns for the audio features DataFrame
        selected_columns = ['id', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']
        audio_features_df = audio_features_df[selected_columns]

        # Merge the playlist DataFrame with the audio features DataFrame
        playlist_with_features = pd.merge(playlist, audio_features_df, on='id', how='inner')
        print("Playlist Tracks:", len(playlist_with_features))

        playlist_with_features = self.rearrange_columns(playlist_with_features)
        
        print('<- sp:analyze_playlist()')
        # Return the resulting DataFrame

        return playlist_with_features
    
    def track_base_features(self, track, track_id):
        """
        Retrieves the audio features of a list of track IDs from Spotify API.

        Args:
            track_id 

        Returns:
            pandas.DataFrame: A DataFrame containing the audio features of the tracks, along with additional information such as artist, name, popularity, and explicitness.
        """
        print("-> sp:get_song_features()")
        # if not track_id:
        #     print("No track provided.")
        #     return
     
        # Retrieve audio features for the track IDs
        audio_features_list = self.sp.audio_features(track_id)

        # Convert the list of audio features into a DataFrame
        audio_features_df = pd.DataFrame(audio_features_list)

        # Select specific columns to print
        selected_columns = ['id', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']

        # Retrieve additional information for each track

        track_features = {
            'artist': track['artists'][0]['name'],
            'id': track['id'],
            'name': track['name'],
            'popularity': track['popularity'],
            'release_date': track['album']['release_date'],
            'artist': track['artists'][0]['name'],
            'artist_url': track['artists'][0]['external_urls']['spotify'],
            'track_image' : track['album']['images'][1]['url']
        }

        # Create a DataFrame for the additional track information
        track_features_df = pd.DataFrame([track_features])


        # Merge the track information DataFrame with the audio features DataFrame
        song_features_df = pd.merge(track_features_df, audio_features_df, on='id', how='inner')

        # Rearrange the columns of the DataFrame
        song_features_df = self.rearrange_columns(song_features_df)
        
        # Add release date if available
        return song_features_df, track_features


    def get_id_type(self, id):
        try:
            track = self.sp.track(id)
            if track:
                return 'track', track
        except:
            pass  # Track not found or an error occurred
        
        try:
            playlist = self.sp.playlist(id)
            if playlist:
                return 'playlist', playlist
        except:
            pass  # Playlist not found or an error occurred

        return 'unknown'

    def rearrange_columns(self, df):
        """
        Rearrange the columns of a DataFrame according to a desired order.

        Parameters:
            df (pandas.DataFrame): The DataFrame to rearrange.

        Returns:
            pandas.DataFrame: The rearranged DataFrame.
        """
        # Define the desired order of columns
        columns_order = ['artist', 'name', 'id', 'date_added', 'popularity', 'duration_ms', 'danceability', 'energy', 'key', 
                         'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 
                         'liveness', 'valence', 'tempo', 'time_signature']

        # Add missing columns with default value 0
        for column in columns_order:
            if column not in df.columns:
                df[column] = 0

        # Reorder the columns
        df = df[columns_order]

        return df

    def get_artist_top_tracks(self, artist_data):
        top_tracks = []
        for artist in artist_data:
            artist_id = artist["artist_id"]
            tracks = self.sp.artist_top_tracks(artist_id, 'US')['tracks']
            for track in tracks:
                top_tracks.append({
                    'name': track['name'],
                    'id': track['id'],
                })
        return top_tracks

    def predict(self, data_entry, choice, class_items):
        print("-> sp:predict()")
        model = class_items['model']
        scaler = class_items['scaler']
        label_encoder = class_items['label_encoder']
        feature_set = class_items['feature_set']

        # Get song features or analyze playlist based on  choice
        if (choice == 'track'):
            data = data_entry
            
        elif (choice == 'playlist'):
                data = self.analyze_playlist(data_entry)
        else:
            raise ValueError("Invalid choice. Expected 'track' or 'playlist'.")
            
        print("Predicting...")

        start_time = time.time()
        # Create a DataFrame from the data
        data_df = pd.DataFrame(data)
        
        # One-hot encode categorical features
        data_df = pd.get_dummies(data_df, columns=['key'], prefix='key')
        
        # Add missing columns to the data DataFrame
        for col in feature_set:
            if col not in data.columns:
                data_df[col] = 0
        
        # Reorder the columns to match the order of the featureset
        data_df = data_df.reindex(columns=feature_set, fill_value=0)

        columns_to_scale = ['popularity', 'duration_ms', 'danceability', 'energy', 'loudness', 
                            'speechiness', 'acousticness', 'instrumentalness', 'liveness', 
                            'valence', 'tempo']
        
        data_df[columns_to_scale] = scaler.transform(data_df[columns_to_scale])
            
        # Predict the genre labels using the model
        predictions_encoded = model.predict(data_df)
        
        # Decode the predicted labels using the label encoder
        predictions_decoded = label_encoder.inverse_transform(predictions_encoded)
        
        # Add the predicted genre labels to the data DataFrame
        data['track_genre'] = predictions_decoded

        if (choice == 'track'):
            # data['release_date'] = release_date
            data.drop('date_added', axis=1, inplace=True)
        
        print("Prediction completed in {:.2f} seconds.".format(time.time() - start_time))
        # Return the data DataFrame with predicted genre labels
        print('<- sp:predict()')

        
        return data

   

    