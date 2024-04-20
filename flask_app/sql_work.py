import os
import mysql.connector
import pandas as pd
import json

class SQLWork:
    def __init__(self):
        self.MYSQL_HOST = os.getenv("MYSQL_HOST")
        self.MYSQL_USER = os.getenv("MYSQL_USER")
        self.MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
        self.MYSQL_DB = os.getenv("MYSQL_DB")
        self.cnx = None

    # Connect to MySQL database
    def connect_sql(self):
        self.cnx = mysql.connector.connect(
            host=self.MYSQL_HOST,
            user=self.MYSQL_USER,
            passwd=self.MYSQL_PASSWORD,
            database=self.MYSQL_DB
        )
            
        
    def get_dataset(self):
        rec_dataset = pd.read_sql("SELECT * FROM rec_dataset", self.cnx)
        rec_dataset = rec_dataset.drop('id', axis=1)
        return rec_dataset
        
    def get_user_data(self, sp):
        
        user_profile, user_playlists, recently_played, top_artists, top_tracks = sp.get_user_saved_info()
        
        unique_id = user_profile['id']
        
        display_name = user_profile['display_name']
        
        email = user_profile['email']
        
        cursor = self.cnx.cursor()

        self.user_profile_db(unique_id, display_name, email)

        self.user_recently_played_db(unique_id, recently_played)

        self.user_playlists_db(unique_id, user_playlists)
        
        self.user_top_artists_db(unique_id, top_artists)

        self.user_top_tracks_db(unique_id, top_tracks)

        return unique_id, display_name
        cursor.close()



    # Helpers        
    def user_profile_db(self, unique_id, display_name, email):
        try:
            cursor = self.cnx.cursor()
            query = "SELECT * FROM users WHERE unique_id = %s"
            cursor.execute(query, (unique_id,))
            result = cursor.fetchone()
            print("User exists")
            if not result:
                print('User does not exist')
                insert_query = "INSERT INTO users (unique_id, display_name, email) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (unique_id, display_name, email))
                cursor.close()
                print('User database authenticated')
            
            self.cnx.commit()
        except mysql.connector.Error as e:
            print(f"Error adding/checking user in database: {e}")

    def user_playlists_db(self, unique_id, user_playlists):
        try:
            cursor = self.cnx.cursor()
            for playlist in user_playlists['items']:
                playlist_id = playlist['id']
                name = playlist['name']
                image_url = playlist['images'][0]['url'] if playlist['images'] else None
                
                query = f"INSERT INTO playlists (playlist_id, unique_id, name, image_url) " \
                        f"SELECT %s, %s, %s, %s " \
                        f"WHERE NOT EXISTS (SELECT 1 FROM playlists WHERE playlist_id = %s AND unique_id = %s);"
                
                cursor.execute(query, (playlist_id, unique_id, name, image_url, playlist_id, unique_id))
            cursor.close()
            print('Playlists added to database')    
            self.cnx.commit()
        except mysql.connector.Error as e:
            print(f"Error adding playlists to database: {e}")

    def user_recently_played_db(self, unique_id, recently_played):
        try:
            cursor = self.cnx.cursor()
            # Recently Played
            query = "DELETE FROM recently_played WHERE unique_id = %s"
            cursor.execute(query, (unique_id,))

            for item in recently_played["items"]:
                track = item["track"]
                artist = track["artists"][0]
                track_id = track["id"]
                track_name = track["name"]
                artist_name = artist["name"]

                insert_query = """
                INSERT INTO recently_played (unique_id, track_id, track_name, artist_name)
                VALUES (%s, %s, %s, %s)
                """
                track_json = json.dumps({'track_id': track_id, 'track_name': track_name, 'artist_name': artist_name})
                cursor.execute(insert_query, (unique_id, track_id, track_name, artist_name))

            cursor.close()
            print('Recently played added to database')
            self.cnx.commit()

        except mysql.connector.Error as e:
            print(f"Error adding recently played to database: {e}")

    def user_top_artists_db(self, unique_id, top_artists):
        try:
            cursor = self.cnx.cursor()
            # Top Artists
            for time_range, artists in top_artists.items():
                for rank, artist in enumerate(artists['items'], start=1):
                    artist_id = artist['id']
                    artist_name = artist['name']

                    # Check if the artist exists for the user
                    check_query = """
                    SELECT COUNT(*) FROM user_top_artists
                    WHERE unique_id = %s AND artist_id = %s
                    """
                    cursor.execute(check_query, (unique_id, artist_id))
                    artist_exists = cursor.fetchone()[0]

                    if artist_exists:
                        # Update the existing row with the new rank
                        update_query = f"""
                        UPDATE user_top_artists
                        SET {time_range}_rank = %s
                        WHERE unique_id = %s AND artist_id = %s
                        """
                        cursor.execute(update_query, (rank, unique_id, artist_id))
                    else:
                        # Insert a new row for the artist
                        insert_query = f"""
                        INSERT INTO user_top_artists (unique_id, artist_id, artist_name, {time_range}_rank)
                        VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (unique_id, artist_id, artist_name, rank))    
            cursor.close()
            print('Top artists added to database')
            self.cnx.commit()

        except mysql.connector.Error as e:
            print(f"Error adding top artists to database: {e}")

    def user_top_tracks_db(self,  unique_id, top_tracks):
        try:
            cursor = self.cnx.cursor()
            # Top Tracks
            for time_range, tracks in top_tracks.items():
                for rank, track in enumerate(tracks['items'], start=1):
                    track_id = track['id']
                    track_name = track['name']
                    artist = track['artists'][0]
                    artist_name = artist['name']
                    # Check if the track exists for the user
                    check_query = """
                    SELECT COUNT(*) FROM user_top_tracks
                    WHERE unique_id = %s AND track_id = %s
                    """
                    cursor.execute(check_query, (unique_id, track_id))
                    track_exists = cursor.fetchone()[0]

                    if track_exists:
                        # Update the existing row with the new rank
                        update_query = f"""
                        UPDATE user_top_tracks
                        SET {time_range}_rank = %s
                        WHERE unique_id = %s AND track_id = %s
                        """
                        cursor.execute(update_query, (rank, unique_id, track_id))
                    else:
                        # Insert a new row for the track
                        insert_query = f"""
                        INSERT INTO user_top_tracks (unique_id, track_id, track_name, artist_name, {time_range}_rank)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (unique_id, track_id, track_name, artist_name, rank))
            cursor.close()
            print('Top tracks added to database')
            self.cnx.commit()

        except mysql.connector.Error as e:
            print(f"Error adding top tracks to database: {e}")
    
    def append_tracks(self, data, append_count):
        cursor = self.cnx.cursor()
        for _, row in data.iterrows():
            query = """
                INSERT INTO append_data (
                    artists, track_name, track_id, popularity, duration_ms,
                    danceability, energy, `key`, loudness, `mode`, speechiness,
                    acousticness, instrumentalness, liveness, valence, tempo,
                    time_signature, track_genre
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                row['artists'], row['track_name'], row['track_id'], row['popularity'],
                row['duration_ms'], row['danceability'], row['energy'], row['key'],
                row['loudness'], row['mode'], row['speechiness'], row['acousticness'],
                row['instrumentalness'], row['liveness'], row['valence'], row['tempo'],
                row['time_signature'], row['track_genre']
            )
            cursor.execute(query, values)
        self.cnx.commit()

        if append_count >= 1:  # Check if conditions for appending to rec_dataset are met
            print('appending')
            query = """
                INSERT INTO rec_dataset (
                    artists, track_name, track_id, popularity, duration_ms,
                    danceability, energy, `key`, loudness, `mode`, speechiness,
                    acousticness, instrumentalness, liveness, valence, tempo,
                    time_signature, track_genre
                )
                SELECT DISTINCT
                    artists, track_name, track_id, popularity, duration_ms,
                    danceability, energy, `key`, loudness, `mode`, speechiness,
                    acousticness, instrumentalness, liveness, valence, tempo,
                    time_signature, track_genre
                FROM append_data
                WHERE track_id NOT IN (SELECT track_id FROM rec_dataset)
            """
            cursor.execute(query)
            query = "TRUNCATE TABLE append_data"
            cursor.execute(query)
            cursor.close()

            self.cnx.commit()
            return True
        else:
            return False



    def get_unique_user_playlist(self, unique_id):
        cursor = self.cnx.cursor()
        query = f"SELECT name, playlist_id FROM playlists WHERE unique_id = '{unique_id}';"    
        cursor.execute(query)
        results = cursor.fetchall()
        return results
        cursor.close()
        
    
    def close_sql(self):
        self.cnx.close()
        print('Connection closed') 
    
