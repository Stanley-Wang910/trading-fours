import os
import mysql.connector.pooling
import pandas as pd
import json

class SQLWork:
    def __init__(self):
        self.MYSQL_HOST = os.getenv("MYSQL_HOST")
        self.MYSQL_USER = os.getenv("MYSQL_USER")
        self.MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
        self.MYSQL_DB = os.getenv("MYSQL_DB")
        self.pool = None

    # Connect to MySQL database
    def connect_sql(self):
        self.pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="pool",
            pool_size=5,
            host=self.MYSQL_HOST,
            user=self.MYSQL_USER,
            passwd=self.MYSQL_PASSWORD,
            database=self.MYSQL_DB
        )
            
    def get_dataset(self):
        connection = self.pool.get_connection()
        try:
            rec_dataset = pd.read_sql("SELECT * FROM rec_dataset", connection)
            rec_dataset = rec_dataset.drop('id', axis=1)
            return rec_dataset
        finally:
            connection.close()
        
    def get_user_data(self, sp):

        user_profile, user_playlists, recently_played, top_artists, top_tracks = sp.get_user_saved_info()
        
        unique_id = user_profile['id']
        
        display_name = user_profile['display_name']
        
        email = user_profile['email']   

        self.user_profile_db(unique_id, display_name, email)

        self.user_recently_played_db(unique_id, recently_played)

        self.user_playlists_db(unique_id, user_playlists)
        
        self.user_top_artists_db(unique_id, top_artists)

        self.user_top_tracks_db(unique_id, top_tracks)

        return unique_id, display_name



    # Helpers        
    def user_profile_db(self, unique_id, display_name, email):
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
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
            
            connection.commit()
        except mysql.connector.Error as e:
            print(f"Error adding/checking user in database: {e}")
        finally:
            cursor.close()
            connection.close()


    def user_playlists_db(self, unique_id, user_playlists): # Maybe add owner_id to filter by current user in playlist dropdwon?
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
            

            # Get the existing playlist IDs from the database for the current user
            query = "SELECT playlist_id FROM playlists WHERE unique_id = %s"
            cursor.execute(query, (unique_id,))
            existing_playlist_ids = [row[0] for row in cursor.fetchall()]
            
            # Get the playlist IDs from the user_playlists items
            user_playlist_ids = [playlist['id'] for playlist in user_playlists['items']]
            
            # Delete playlists from the database if they are not found in the user_playlists items
            playlist_ids_to_delete = set(existing_playlist_ids) - set(user_playlist_ids)
            if playlist_ids_to_delete:
                delete_query = "DELETE FROM playlists WHERE playlist_id IN ({})".format(
                    ','.join(['%s'] * len(playlist_ids_to_delete))
                )
                cursor.execute(delete_query, tuple(playlist_ids_to_delete))
                print(f"Deleted {cursor.rowcount} playlists from the database")

            for playlist in user_playlists['items']:
                playlist_id = playlist['id']
                name = playlist['name']
                image_url = playlist['images'][0]['url'] if playlist['images'] else None
                
                query = f"INSERT INTO playlists (playlist_id, unique_id, name, image_url) " \
                        f"SELECT %s, %s, %s, %s " \
                        f"WHERE NOT EXISTS (SELECT 1 FROM playlists WHERE playlist_id = %s AND unique_id = %s);"
                
                cursor.execute(query, (playlist_id, unique_id, name, image_url, playlist_id, unique_id))
            print('Playlists added to database')    
            connection.commit()
        except mysql.connector.Error as e:
            print(f"Error adding playlists to database: {e}")
        finally:
            cursor.close()
            connection.close()

    def user_recently_played_db(self, unique_id, recently_played):
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
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
    
            print('Recently played added to database')
            connection.commit()
    
        except mysql.connector.Error as e:
            print(f"Error adding recently played to database: {e}")
        finally:
            cursor.close()
            connection.close()

    def user_top_artists_db(self, unique_id, top_artists):
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
            # Top Artists
            for time_range, artists in top_artists.items():
                clear_query = """
                UPDATE user_top_artists
                SET {}_rank = NULL
                WHERE unique_id = %s
                """.format(time_range)
                cursor.execute(clear_query, (unique_id,))

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
                        update_query = """
                        UPDATE user_top_artists
                        SET {}_rank = %s
                        WHERE unique_id = %s AND artist_id = %s
                        """.format(time_range)
                        cursor.execute(update_query, (rank, unique_id, artist_id))
                    else:
                        # Insert a new row for the artist
                        insert_query = """
                        INSERT INTO user_top_artists (unique_id, artist_id, artist_name, {}_rank)
                        VALUES (%s, %s, %s, %s)
                        """.format(time_range)
                        cursor.execute(insert_query, (unique_id, artist_id, artist_name, rank))    
            delete_query = """
            DELETE FROM user_top_artists
            WHERE unique_id = %s
            AND short_term_rank IS NULL
            AND medium_term_rank IS NULL
            AND long_term_rank IS NULL
            """
            
            print('Top artists added to database')
            connection.commit()

        except mysql.connector.Error as e:
            print(f"Error adding top artists to database: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def user_top_tracks_db(self, unique_id, top_tracks):
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
            # Top Tracks
            for time_range, tracks in top_tracks.items():
                clear_query = """
                UPDATE user_top_tracks
                SET {}_rank = NULL
                WHERE unique_id = %s
                """.format(time_range)
                cursor.execute(clear_query, (unique_id,))

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
                        update_query = """
                        UPDATE user_top_tracks
                        SET {}_rank = %s
                        WHERE unique_id = %s AND track_id = %s
                        """.format(time_range)
                        cursor.execute(update_query, (rank, unique_id, track_id))
                    else:
                        # Insert a new row for the track
                        insert_query = """
                        INSERT INTO user_top_tracks (unique_id, track_id, track_name, artist_name, {}_rank)
                        VALUES (%s, %s, %s, %s, %s)
                        """.format(time_range)
                        cursor.execute(insert_query, (unique_id, track_id, track_name, artist_name, rank))
            
            # Delete tracks with null rankings in all three categories for the user
            delete_query = """
            DELETE FROM user_top_tracks
            WHERE unique_id = %s
            AND short_term_rank IS NULL
            AND medium_term_rank IS NULL
            AND long_term_rank IS NULL
            """
            cursor.execute(delete_query, (unique_id,))
            
            
            print('Top tracks added to database')
            connection.commit()
    
        except mysql.connector.Error as e:
            print(f"Error adding top tracks to database: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()
    
    def append_tracks(self, data, append_count):
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
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
            connection.commit()
            query = "SELECT COUNT(*) FROM append_data"
            cursor.execute(query)
            row_count = cursor.fetchone()[0]

            if append_count >= 20 or row_count > 500:  # Check if conditions for appending to rec_dataset are met
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
                connection.commit()
                return True
            else:
                return False
        finally:
            cursor.close()
            connection.close()

    def get_unique_user_playlist(self, unique_id):
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
            query = f"SELECT name, playlist_id, image_url, unique_id FROM playlists WHERE unique_id = '{unique_id}';"    
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        finally:
            cursor.close()
            connection.close()


    def add_liked_tracks(self, unique_id, rec_id, liked_track_ids):
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
            for track_id in liked_track_ids:
                query = """
                    INSERT INTO user_liked (unique_id, rec_id, track_id)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (unique_id, rec_id, track_id))
            connection.commit()
            print('Liked tracks added to database')
        except mysql.connector.Error as e:
            print(f"Error adding liked tracks to database: {e}")
        finally:
            cursor.close()
            connection.close()

    def add_vector_to_db(self, vector, id, type_id):
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()

            values = (
                id, 
                vector['acousticness'], vector['danceability'], vector['duration_ms'],
                vector['energy'], vector['instrumentalness'], vector['key_0'], vector['key_1'],
                vector['key_10'], vector['key_11'], vector['key_2'], vector['key_3'],
                vector['key_4'], vector['key_5'], vector['key_6'], vector['key_7'],
                vector['key_8'], vector['key_9'], vector['liveness'], vector['loudness'],
                vector['mode_0'], vector['mode_1'], vector['popularity'], vector['speechiness'],
                vector['tempo'], vector['time_signature'], vector['track_genre_Alternative'],
                vector['track_genre_Anime'], vector['track_genre_Blues'], vector['track_genre_Classical'],
                vector['track_genre_Country'], vector['track_genre_Dance'], vector['track_genre_Electronic'],
                vector['track_genre_Folk'], vector['track_genre_Hip-Hop'], vector['track_genre_Indie'],
                vector['track_genre_Jazz'], vector['track_genre_Opera'], vector['track_genre_Pop'],
                vector['track_genre_R&B'], vector['track_genre_Reggae'], vector['track_genre_Reggaeton'],
                vector['track_genre_Rock'], vector['track_genre_Soul'], vector['track_genre_Soundtrack'],
                vector['track_genre_World'], vector['valence']
                )
            
            if type_id == 'playlist':
                check_query = "SELECT COUNT(*) FROM playlist_vectors WHERE playlist_id = %s"
                cursor.execute(check_query, (id,))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    # If the playlist vector exists, update it
                    update_query = """
                        UPDATE playlist_vectors SET
                            acousticness = %s, danceability = %s, duration_ms = %s, energy = %s,
                            instrumentalness = %s, key_0 = %s, key_1 = %s, key_10 = %s, key_11 = %s,
                            key_2 = %s, key_3 = %s, key_4 = %s, key_5 = %s, key_6 = %s, key_7 = %s,
                            key_8 = %s, key_9 = %s, liveness = %s, loudness = %s, mode_0 = %s,
                            mode_1 = %s, popularity = %s, speechiness = %s, tempo = %s,
                            time_signature = %s, track_genre_Alternative = %s, track_genre_Anime = %s,
                            track_genre_Blues = %s, track_genre_Classical = %s, track_genre_Country = %s,
                            track_genre_Dance = %s, track_genre_Electronic = %s, track_genre_Folk = %s,
                            track_genre_Hip_Hop = %s, track_genre_Indie = %s, track_genre_Jazz = %s,
                            track_genre_Opera = %s, track_genre_Pop = %s, track_genre_R_B = %s,
                            track_genre_Reggae = %s, track_genre_Reggaeton = %s, track_genre_Rock = %s,
                            track_genre_Soul = %s, track_genre_Soundtrack = %s, track_genre_World = %s,
                            valence = %s
                        WHERE playlist_id = %s
                        """
                    cursor.execute(update_query, values[1:] + (id,))
                    print(f"Playlist vector updated in the 'playlist_vectors' table for playlist ID: {id}")
                else:
                    insert_query = """
                        INSERT INTO playlist_vectors (
                            playlist_id, acousticness, danceability, duration_ms, energy,
                            instrumentalness, key_0, key_1, key_10, key_11, key_2, key_3,
                            key_4, key_5, key_6, key_7, key_8, key_9, liveness, loudness,
                            mode_0, mode_1, popularity, speechiness, tempo, time_signature,
                            track_genre_Alternative, track_genre_Anime, track_genre_Blues,
                            track_genre_Classical, track_genre_Country, track_genre_Dance,
                            track_genre_Electronic, track_genre_Folk, track_genre_Hip_Hop,
                            track_genre_Indie, track_genre_Jazz, track_genre_Opera,
                            track_genre_Pop, track_genre_R_B, track_genre_Reggae,
                            track_genre_Reggaeton, track_genre_Rock, track_genre_Soul,
                            track_genre_Soundtrack, track_genre_World, valence
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s)
                        """

                    cursor.execute(insert_query, values)
                    print(f"New playlist vector inserted into the 'playlist_vectors' table for playlist ID: {id}")
            
            elif type_id == 'track':

                check_query = "SELECT COUNT(*) FROM track_vectors WHERE track_id = %s"
                cursor.execute(check_query, (id,))
                count = cursor.fetchone()[0]

                if count > 0:
                    print(f"Track vector already exists in the 'track_vectors' table for track ID: {id}")
                
                else:
                    insert_query = """
                        INSERT INTO track_vectors (
                            track_id, acousticness, danceability, duration_ms, energy,
                            instrumentalness, key_0, key_1, key_10, key_11, key_2, key_3,
                            key_4, key_5, key_6, key_7, key_8, key_9, liveness, loudness,
                            mode_0, mode_1, popularity, speechiness, tempo, time_signature,
                            track_genre_Alternative, track_genre_Anime, track_genre_Blues,
                            track_genre_Classical, track_genre_Country, track_genre_Dance,
                            track_genre_Electronic, track_genre_Folk, track_genre_Hip_Hop,
                            track_genre_Indie, track_genre_Jazz, track_genre_Opera,
                            track_genre_Pop, track_genre_R_B, track_genre_Reggae,
                            track_genre_Reggaeton, track_genre_Rock, track_genre_Soul,
                            track_genre_Soundtrack, track_genre_World, valence
                        )
                        
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s)
                        """
                    cursor.execute(insert_query, values)
                    print(f"New track vector inserted into the 'track_vectors' table for track ID: {id}")
            connection.commit()
        except mysql.connector.Error as e:
            print(f"Error adding vector to database: {e}")
        finally:
            cursor.close()
            connection.close()
    
    def get_vector_from_db(self, id, type_id):
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
            if type_id == 'playlist':
                query = f"SELECT * FROM playlist_vectors WHERE playlist_id = '{id}'"
                columns = [
                    'playlist_id', 'acousticness', 'danceability', 'duration_ms', 'energy',
                    'instrumentalness', 'key_0', 'key_1', 'key_10', 'key_11', 'key_2', 'key_3',
                    'key_4', 'key_5', 'key_6', 'key_7', 'key_8', 'key_9', 'liveness', 'loudness',
                    'mode_0', 'mode_1', 'popularity', 'speechiness', 'tempo', 'time_signature',
                    'track_genre_Alternative', 'track_genre_Anime', 'track_genre_Blues',
                    'track_genre_Classical', 'track_genre_Country', 'track_genre_Dance',
                    'track_genre_Electronic', 'track_genre_Folk', 'track_genre_Hip_Hop',
                    'track_genre_Indie', 'track_genre_Jazz', 'track_genre_Opera',
                    'track_genre_Pop', 'track_genre_R_B', 'track_genre_Reggae',
                    'track_genre_Reggaeton', 'track_genre_Rock', 'track_genre_Soul',
                    'track_genre_Soundtrack', 'track_genre_World', 'valence'
                ]
            elif type_id == 'track':
                query = f"SELECT * FROM track_vectors WHERE track_id = '{id}'"
                columns = [
                    'track_id', 'acousticness', 'danceability', 'duration_ms', 'energy',
                    'instrumentalness', 'key_0', 'key_1', 'key_10', 'key_11', 'key_2', 'key_3',
                    'key_4', 'key_5', 'key_6', 'key_7', 'key_8', 'key_9', 'liveness', 'loudness',
                    'mode_0', 'mode_1', 'popularity', 'speechiness', 'tempo', 'time_signature',
                    'track_genre_Alternative', 'track_genre_Anime', 'track_genre_Blues',
                    'track_genre_Classical', 'track_genre_Country', 'track_genre_Dance',
                    'track_genre_Electronic', 'track_genre_Folk', 'track_genre_Hip_Hop',
                    'track_genre_Indie', 'track_genre_Jazz', 'track_genre_Opera',
                    'track_genre_Pop', 'track_genre_R_B', 'track_genre_Reggae',
                    'track_genre_Reggaeton', 'track_genre_Rock', 'track_genre_Soul',
                    'track_genre_Soundtrack', 'track_genre_World', 'valence'
                ]
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                vector = pd.DataFrame([result], columns=columns)
                
                # Rename columns
                vector = vector.rename(columns={
                    'track_genre_R_B': 'track_genre_R&B',
                    'track_genre_Hip_Hop': 'track_genre_Hip-Hop'
                })
                
                # Drop the 'playlist_id' or 'track_id' column
                if type_id == 'playlist':
                    vector = vector.drop(columns=['playlist_id'])
                elif type_id == 'track':
                    vector = vector.drop(columns=['track_id'])
                print(f"Vector retrieved from {'playlist_vectors' if type_id == 'playlist' else 'track_vectors'} table.")
                return vector
            else:
                return None
        except mysql.connector.Error as e:
            print(f"Error getting vector from database: {e}")
        finally:
            cursor.close()
            connection.close()

    def get_user_top_tracks(self, unique_id):
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
            query = f"SELECT * FROM user_top_tracks WHERE unique_id = '{unique_id}'"
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
        
            # Create a list of dictionaries with column names as keys
            output = []
            for row in results:
                row_dict = {column_names[i]: value for i, value in enumerate(row)}
                output.append(row_dict)
            
            print('User top tracks retrieved from database')
            return output
        except mysql.connector.Error as e:
            print(f"Error retrieving user top tracks from database: {e}")
        finally:
            cursor.close()
            connection.close()

    def get_user_top_artists(self, unique_id):
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
            query = f"SELECT * FROM user_top_artists WHERE unique_id = '{unique_id}'"
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
        
            # Create a list of dictionaries with column names as keys
            output = []
            for row in results:
                row_dict = {column_names[i]: value for i, value in enumerate(row)}
                output.append(row_dict)
            
            print('User top artists retrieved from database')
            return output
        except mysql.connector.Error as e:
            print(f"Error retrieving user top artists from database: {e}")
        finally:
            cursor.close()
            connection.close()
    
    def get_user_recently_played(self, unique_id):
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
            query = f"SELECT * FROM recently_played WHERE unique_id = '{unique_id}'"
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
        
            # Create a list of dictionaries with column names as keys
            output = []
            for row in results:
                row_dict = {column_names[i]: value for i, value in enumerate(row)}
                output.append(row_dict)
            
            print('User recently played tracks retrieved from database')
            return output
        except mysql.connector.Error as e:
            print(f"Error retrieving user recently played tracks from database: {e}")
        finally:
            cursor.close()
            connection.close()

    def get_tracks_by_artists(self, artist_names):
        connection = self.pool.get_connection()
        try:
            placeholders = ', '.join(['%s'] * len(artist_names))
            query = f"""
                SELECT * FROM rec_dataset
                WHERE artists IN ({placeholders})
            """
            cursor = connection.cursor()
            cursor.execute(query, artist_names)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            tracks_df = pd.DataFrame(results, columns=columns)
            return tracks_df
        except mysql.connector.Error as e:
            print(f"Error getting tracks by artists from database: {e}")
        finally:
            cursor.close()
            connection.close()
            

       
    
    def close_sql(self):
        self.pool.closeall()
        print('All connections in pool closed')
