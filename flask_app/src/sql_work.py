import os
from dotenv import load_dotenv
import mysql.connector.pooling
import pandas as pd
import json
import time
import mysql.connector
from contextlib import contextmanager   

load_dotenv()

class SQLWork:
    def __init__(self):
        self.MYSQL_HOST = os.environ.get('MYSQL_HOST')
        self.MYSQL_USER = os.environ.get('MYSQL_USER')
        self.MYSQL_PORT = os.environ.get('MYSQL_PORT')
        print(self.MYSQL_USER)
        print(self.MYSQL_HOST)  
        self.MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
        self.MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
        print(self.MYSQL_DATABASE)
        try:
            self.pool =  mysql.connector.pooling.MySQLConnectionPool(
                host=self.MYSQL_HOST,
                port=self.MYSQL_PORT,
                user=self.MYSQL_USER,
                passwd=self.MYSQL_PASSWORD,
                database=self.MYSQL_DATABASE,
                pool_name="pool",
                pool_size=5,
            )
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e}")
        
    @contextmanager
    def get_cursor(self):
        connection = self.pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            yield cursor
            connection.commit()
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()



    def get_dataset(self, top_genres, user_top_artists=None, track=False, artist_rec=False):
        print("-> get_dataset()")
        retries = 5 
        while retries > 0:
            try: 
                with self.get_cursor() as cursor:
                    if track == False:
                        if artist_rec == False:
                            print(top_genres)
                            print([artist['artist_name'] for artist in user_top_artists])
                            query = """
                            SELECT * FROM rec_dataset WHERE artists IN ({}) OR track_genre IN ({})
                            """.format(
                                ','.join(['%s'] * len([artist['artist_name'] for artist in user_top_artists])),
                                ','.join(['%s'] * len(top_genres))
                            )
                            # Flatten list of genre and artiist names to use as parameters
                            params = [artist['artist_name'] for artist in user_top_artists] + top_genres
                        else:
                            query = """SELECT * FROM rec_dataset 
                            WHERE artists IN ({}) AND track_genre NOT IN ({})
                            """.format(
                                ','.join(['%s'] * len(user_top_artists)),
                                ','.join(['%s'] * len(top_genres))
                            )
                            params = user_top_artists + top_genres
                    else:
                        print("track = True")
                        query = """SELECT * FROM rec_dataset WHERE track_genre = %s"""
                        params = [top_genres]

                    cursor.execute(query, params)
                    rec_dataset = pd.DataFrame(cursor.fetchall())
                    if 'id' in rec_dataset.columns:
                        rec_dataset = rec_dataset.drop('id', axis=1)
                    return rec_dataset
            except mysql.connector.Error as e:
                print(f"Error getting dataset from database: {e}")
                retries -= 1
                print(f"Retries left: {retries}")
                time.sleep(5)
            except Exception as e:
                print(f"Unexpected error: {e}")
                retries -= 1
                print(f"Retries left: {retries}")
                time.sleep(5)
            finally:
                if 'connection' in locals() and connection.is_connected():
                    connection.close()
                    print("Connection closed.")
        print("Failed to get dataset after multiple retries.")
        return None

           
    # def get_dataset(self):
    #     print("-> get_dataset()")
    #     retries = 5 
    #     while retries > 0:
    #         try: 
    #             connection = self.pool.get_connection()

    #             rec_dataset = pd.read_sql("SELECT * FROM rec_dataset", connection)
    #             rec_dataset = rec_dataset.drop('id', axis=1)
    #             return rec_dataset
    #         except mysql.connector.Error as e:
    #             print(f"Error getting dataset from database: {e}")
    #             retries -= 1
    #             print(f"Retries left: {retries}")
    #             time.sleep(5)
    #         except Exception as e:
    #             print(f"Unexpected error: {e}")
    #             retries -= 1
    #             print(f"Retries left: {retries}")
    #             time.sleep(5)
    #         finally:
    #             if 'connection' in locals() and connection.is_connected():
    #                 connection.close()
    #                 print("Connection closed.")
    #     print("Failed to get dataset after multiple retries.")
    #     return None
        
    def get_user_data(self, sp):
        
        start_time = time.time()

        user_profile, user_playlists, top_artists, top_tracks = sp.get_user_saved_info()
        
        print("Getting user data from sp... :", time.time() - start_time, "s")
        
        unique_id = user_profile['id']
        
        display_name = user_profile['display_name']
        
        email = user_profile['email']  

        if unique_id == "31bv2bralifp3lgy4p5zvikjghki" :
            return unique_id, display_name

        start_time = time.time()
        self.user_profile_db(unique_id, display_name, email)

        print("Saving user profile to database... :", time.time() - start_time, "s")
        

        # self.user_recently_played_db(unique_id, recently_played)

 

        start_time = time.time()

        self.user_playlists_db(unique_id, user_playlists)
        print("Saving user playlists to database...", time.time() - start_time, "s")
        start_time = time.time()
        
        self.user_top_artists_db(unique_id, top_artists)

        print("Saving user top artists to database... :", time.time() - start_time, "s")

        start_time = time.time()

        self.user_top_tracks_db(unique_id, top_tracks)

        print("Saving user top tracks to database... :", time.time() - start_time, "s")

        print("User data saved to database")

        return unique_id, display_name



    # Helpers        
    def user_profile_db(self, unique_id, display_name, email):

        print("-> user_profile_db()")

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
            print('<- user_profile_db()')
            cursor.close()
            connection.close()


    def user_playlists_db(self, unique_id, user_playlists): # Maybe add owner_id to filter by current user in playlist dropdwon?
        try:
            with self.get_cursor() as cursor:
                # Get existing playlist IDs from the database for the current user
                cursor.execute("SELECT playlist_id, name, image_url, owner_id FROM playlists WHERE unique_id = %s", (unique_id,))
                existing_playlists = {row['playlist_id']: row for row in cursor.fetchall()}
                
                # Prepare data for batch operations
                user_playlist_ids = set()
                update_data = []
                insert_data = []

                for playlist in user_playlists:
                    playlist_id = playlist['id']
                    user_playlist_ids.add(playlist_id)
                    name = playlist['name'] 
                    image_url = playlist['images'][0]['url'] if playlist['images'] else None
                    owner_id = playlist['owner']['id']

                    if playlist_id in existing_playlists:
                        existing = existing_playlists[playlist_id]
                        if (name != existing['name'] or 
                            image_url != existing['image_url'] or 
                            owner_id != existing['owner_id']):
                            update_data.append((name, image_url, owner_id, unique_id, playlist_id))
                            print(f"Updating playlist: {playlist_id}, Name: {name}")
                    else:
                        insert_data.append((playlist_id, name, image_url, owner_id, unique_id))

                playlists_to_delete = set(existing_playlists.keys()) - user_playlist_ids
                if playlists_to_delete:
                    delete_query = "DELETE FROM playlists WHERE unique_id = %s AND playlist_id IN ({})".format(
                        ','.join(['%s'] * len(playlists_to_delete))
                    )
                    cursor.execute(delete_query, (unique_id, *playlists_to_delete))
                    print(f"Deleted {cursor.rowcount} playlists from the database")

                print("Update Data:", update_data)
                # Batch update existing playlists
                if update_data:
                    update_query = """
                    UPDATE playlists
                    SET name = %s, image_url = %s, owner_id = %s
                    WHERE unique_id = %s AND playlist_id = %s
                    """
                    cursor.executemany(update_query, update_data)
                    print(f"Updated {cursor.rowcount} playlists in the database")

                # Batch insert new playlists
                      # Insert new playlists
                if insert_data:
                    insert_query = """
                    INSERT INTO playlists (playlist_id, name, image_url, owner_id, unique_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    try:
                        cursor.executemany(insert_query, insert_data)
                        print(f"Inserted {cursor.rowcount} new playlists into the database")
                    except mysql.connector.IntegrityError as e:
                        if e.errno == 1062:  # Duplicate entry error
                            print("Duplicate playlist entry encountered. Inserting playlists one by one.")
                            for playlist_data in insert_data:
                                try:
                                    cursor.execute(insert_query, playlist_data)
                                except mysql.connector.IntegrityError as inner_e:
                                    if inner_e.errno == 1062:
                                        print(f"Skipping duplicate playlist: {playlist_data[0]}")
                                    else:
                                        raise
                        else:
                            raise

            print('Playlists synchronized with database')
        except mysql.connector.Error as e:
            print(f"Error adding playlists to database: {e}")
            raise


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
        try:
            with self.get_cursor() as cursor:
                # Fetch existing artists for logging purposes
                cursor.execute("""
                    SELECT artist_id, artist_name, short_term_rank 
                    FROM user_top_artists 
                    WHERE unique_id = %s
                """, (unique_id,))
                existing_artists = {row['artist_id']: row for row in cursor.fetchall()}

                # Prepare data for upsert operation
                upsert_data = []
                all_artist_ids = set()

                for time_range, artists in top_artists.items():
                    for rank, artist in enumerate(artists['items'], start=1):
                        artist_id = artist['id']
                        artist_name = artist['name']
                        all_artist_ids.add(artist_id)

                        # Prepare data for upsert
                        upsert_data.append((
                            unique_id, artist_id, artist_name,
                            rank if time_range == 'short_term' else None,
                            # rank if time_range == 'medium_term' else None,
                            # rank if time_range == 'long_term' else None
                        ))

                        # Log changes
                        if artist_id in existing_artists:
                            old_rank = existing_artists[artist_id][f'{time_range}_rank']
                            if old_rank != rank:
                                print(f"Artist {artist_name} {time_range}_rank: {old_rank} -> {rank}")
                        else:
                            print(f"New artist {artist_name} {time_range}_rank: None -> {rank}")

                # Perform upsert operation
                upsert_query = """
                    INSERT INTO user_top_artists 
                        (unique_id, artist_id, artist_name, short_term_rank)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        artist_name = VALUES(artist_name),
                        short_term_rank = VALUES(short_term_rank)
                """
                cursor.executemany(upsert_query, upsert_data)
                
                print(f'Artists upserted: {len(upsert_data)}')

                # Update ranks to NULL for artists no longer in any top list
                print(existing_artists.keys())
                artists_to_update = set(existing_artists.keys()) - all_artist_ids
                if artists_to_update:
                    placeholders = ','.join(['%s'] * len(artists_to_update))
                    null_update_query = f"""
                        DELETE FROM user_top_artists
                        WHERE unique_id = %s AND artist_id IN ({placeholders})
                    """
                    params = [unique_id] + list(artists_to_update)
                    cursor.execute(null_update_query, params)
                    
                    for artist_id in artists_to_update:
                        artist = existing_artists[artist_id]
                        print(f"Removing artist {artist['artist_name']} from table")

                print(f'Top artists updated: {len(upsert_data)} upserted, {len(artists_to_update)} removed from table')

        except mysql.connector.Error as e:
            print(f"Error updating top artists in database: {e}")
            raise


    def user_top_tracks_db(self, unique_id, top_tracks):
        try:
            with self.get_cursor() as cursor:

                cursor.execute("""
                    SELECT track_id, track_name, artist_name, short_term_rank
                    FROM user_top_tracks
                    WHERE unique_id = %s
                """, (unique_id,))
                existing_tracks = {row['track_id']: row for row in cursor.fetchall()}

                # Prepare data for upsert operation
                upsert_data = []
                all_track_ids = set()

                for time_range, tracks in top_tracks.items():
                    for rank, track in enumerate(tracks['items'], start=1):
                        track_id = track['id']
                        track_name = track['name']
                        artist = track['artists'][0]
                        artist_name = artist['name']
                        all_track_ids.add(track_id)

                        # Prepare data for upsert
                        upsert_data.append((
                            unique_id, track_id, track_name, artist_name,
                            rank if time_range == 'short_term' else None,
                            # rank if time_range == 'medium_term' else None,
                            # rank if time_range == 'long_term' else None
                        ))

                        # Log changes
                        if track_id in existing_tracks:
                            old_rank = existing_tracks[track_id][f'{time_range}_rank']
                            if old_rank != rank:
                                print(f"Track {track_name} {time_range}_rank: {old_rank} -> {rank}")
                        else:
                            print(f"New track {track_name} {time_range}_rank: None -> {rank}")

                # Perform upsert operation
                upsert_query = """
                    INSERT INTO user_top_tracks
                        (unique_id, track_id, track_name, artist_name, short_term_rank)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        track_name = VALUES(track_name),
                        artist_name = VALUES(artist_name),
                        short_term_rank = VALUES(short_term_rank)
                    """
                cursor.executemany(upsert_query, upsert_data)

                print(f'Top tracks upserted: {len(upsert_data)}')

                # Update ranks to NULL for tracks no longer in any top list
                tracks_to_update = set(existing_tracks.keys()) - all_track_ids
                if tracks_to_update:
                    placeholders = ','.join(['%s'] * len(tracks_to_update))
                    null_update_query = f"""
                        DELETE FROM user_top_tracks
                        WHERE unique_id = %s AND track_id IN ({placeholders})
                    """
                    
                    params = [unique_id] + list(tracks_to_update)
                    cursor.execute(null_update_query, params)
                    
                    for track_id in tracks_to_update:
                        track = existing_tracks[track_id] 
                        print(f"Removing track {track['track_name']} from top lists")

                print(f'Top tracks updated: {len(upsert_data)} upserted, {len(tracks_to_update)} removed from table')
        
        except mysql.connector.Error as e:
            print(f"Error updating top tracks in database: {e}")
            raise
        
    
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
            query = """
                SELECT name, playlist_id, image_url, unique_id, owner_id
                FROM playlists 
                WHERE unique_id = %s
                ORDER BY CASE WHEN owner_id = %s THEN 0 ELSE 1 END;

                """    
            cursor.execute(query, (unique_id, unique_id))
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

    def add_vector_to_db(self, vector, playlist_id):
        vector = vector.rename(columns={
            'track_genre_R&B': 'track_genre_R_B',
            'track_genre_Hip-Hop': 'track_genre_Hip_Hop'
        })

        if isinstance(vector, pd.DataFrame):
            vector = vector.iloc[0].to_dict()

        vector['playlist_id'] = playlist_id
        upsert_query ="""
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
        ) VALUES (
            %(playlist_id)s, %(acousticness)s, %(danceability)s, %(duration_ms)s, %(energy)s,
            %(instrumentalness)s, %(key_0)s, %(key_1)s, %(key_10)s, %(key_11)s, %(key_2)s, %(key_3)s,
            %(key_4)s, %(key_5)s, %(key_6)s, %(key_7)s, %(key_8)s, %(key_9)s, %(liveness)s, %(loudness)s,
            %(mode_0)s, %(mode_1)s, %(popularity)s, %(speechiness)s, %(tempo)s, %(time_signature)s,
            %(track_genre_Alternative)s, %(track_genre_Anime)s, %(track_genre_Blues)s,
            %(track_genre_Classical)s, %(track_genre_Country)s, %(track_genre_Dance)s,
            %(track_genre_Electronic)s, %(track_genre_Folk)s, %(track_genre_Hip_Hop)s,
            %(track_genre_Indie)s, %(track_genre_Jazz)s, %(track_genre_Opera)s,
            %(track_genre_Pop)s, %(track_genre_R_B)s, %(track_genre_Reggae)s,
            %(track_genre_Reggaeton)s, %(track_genre_Rock)s, %(track_genre_Soul)s,
            %(track_genre_Soundtrack)s, %(track_genre_World)s, %(valence)s
        ) ON DUPLICATE KEY UPDATE
            acousticness = VALUES(acousticness),
            danceability = VALUES(danceability),
            duration_ms = VALUES(duration_ms),
            energy = VALUES(energy),
            instrumentalness = VALUES(instrumentalness),
            key_0 = VALUES(key_0),
            key_1 = VALUES(key_1),
            key_10 = VALUES(key_10),
            key_11 = VALUES(key_11),
            key_2 = VALUES(key_2),
            key_3 = VALUES(key_3),
            key_4 = VALUES(key_4),
            key_5 = VALUES(key_5),
            key_6 = VALUES(key_6),
            key_7 = VALUES(key_7),
            key_8 = VALUES(key_8),
            key_9 = VALUES(key_9),
            liveness = VALUES(liveness),
            loudness = VALUES(loudness),
            mode_0 = VALUES(mode_0),
            mode_1 = VALUES(mode_1),
            popularity = VALUES(popularity),
            speechiness = VALUES(speechiness),
            tempo = VALUES(tempo),
            time_signature = VALUES(time_signature),
            track_genre_Alternative = VALUES(track_genre_Alternative),
            track_genre_Anime = VALUES(track_genre_Anime),
            track_genre_Blues = VALUES(track_genre_Blues),
            track_genre_Classical = VALUES(track_genre_Classical),
            track_genre_Country = VALUES(track_genre_Country),
            track_genre_Dance = VALUES(track_genre_Dance),
            track_genre_Electronic = VALUES(track_genre_Electronic),
            track_genre_Folk = VALUES(track_genre_Folk),
            track_genre_Hip_Hop = VALUES(track_genre_Hip_Hop),
            track_genre_Indie = VALUES(track_genre_Indie),
            track_genre_Jazz = VALUES(track_genre_Jazz),
            track_genre_Opera = VALUES(track_genre_Opera),
            track_genre_Pop = VALUES(track_genre_Pop),
            track_genre_R_B = VALUES(track_genre_R_B),
            track_genre_Reggae = VALUES(track_genre_Reggae),
            track_genre_Reggaeton = VALUES(track_genre_Reggaeton),
            track_genre_Rock = VALUES(track_genre_Rock),
            track_genre_Soul = VALUES(track_genre_Soul),
            track_genre_Soundtrack = VALUES(track_genre_Soundtrack),
            track_genre_World = VALUES(track_genre_World),
            valence = VALUES(valence)
        """
        with self.get_cursor() as cursor:
            cursor.execute(upsert_query, vector)
            print(f"Playlist vector upserted for playlist ID: {playlist_id}")

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
    
    def update_user_recommendation_count(self, unique, recommendation_count):
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
            query = "UPDATE users SET rec_count = rec_count + %s WHERE unique_id = %s"
            cursor.execute(query, (recommendation_count, unique))
            connection.commit()
            print('User recommendation count updated in database')
        except mysql.connector.Error as e:
            print(f"Error updating user recommendation count in database: {e}")
        finally:
            cursor.close()
            connection.close()

    def get_playlist_vectors(self): 
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM playlist_vectors")
                playlist_vectors = pd.DataFrame(cursor.fetchall())

                playlist_vectors = playlist_vectors.rename(columns={
                    'track_genre_R_B': 'track_genre_R&B',
                    'track_genre_Hip_Hop': 'track_genre_Hip-Hop'
                })
            return playlist_vectors
        except mysql.connector.Error as e:
            print(f"Error getting playlist vectors from database: {e}")
            raise

    
    def close_sql(self):
        self.pool.closeall()
        print('All connections in pool closed')

    def assert_hers(self, unique_id):
        with self.get_cursor() as cursor:
            cursor.execute("SELECT unique_id FROM users where display_name = 'lydialepki'")
            hid = cursor.fetchone()
            hid = hid['unique_id']
            if hid is not None:
                return unique_id == hid
