import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os

df = pd.read_csv('data/datasets/rec_dataset.csv')

load_dotenv()
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

db = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    passwd=MYSQL_PASSWORD,
    database=MYSQL_DB
)

cursor = db.cursor()
create_table_query = """
CREATE TABLE IF NOT EXISTS rec_dataset (
    id INT AUTO_INCREMENT PRIMARY KEY,
    artists VARCHAR(255),
    track_name VARCHAR(255),
    track_id VARCHAR(255),
    popularity INT,
    duration_ms INT,
    danceability FLOAT,
    energy FLOAT,
    `key` INT,
    loudness FLOAT,
    mode INT,
    speechiness FLOAT,
    acousticness FLOAT,
    instrumentalness FLOAT,
    liveness FLOAT,
    valence FLOAT,
    tempo FLOAT,
    time_signature FLOAT,
    track_genre VARCHAR(255)
)
"""
cursor.execute(create_table_query)

values = []
for i, row in df.iterrows():
    max_length = 255  # replace with the actual max length of your 'artists' column
    row['artists'] = str(row['artists'])[:max_length]
    row['track_name'] = str(row['track_name'])[:max_length]
    row_values = (row['artists'], row['track_name'], row['track_id'], row['popularity'],
                row['duration_ms'], row['danceability'], row['energy'], row['key'],
                row['loudness'], row['mode'], row['speechiness'], row['acousticness'],
                row['instrumentalness'], row['liveness'], row['valence'], row['tempo'],
                row['time_signature'], row['track_genre'])
    row_values = tuple(None if pd.isna(val) else val for val in row_values)
    values.append(row_values)
insert_query = """
INSERT INTO rec_dataset (artists, track_name, track_id, popularity,
                             duration_ms, danceability, energy, `key`, 
                             loudness, mode, speechiness, acousticness, 
                             instrumentalness, liveness, valence, tempo, 
                             time_signature, track_genre)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
try:
    cursor.executemany(insert_query, values)
except mysql.connector.DataError as e:
    print(f"Error inserting row: {row}")
    raise e
db.commit()
cursor.close()
db.close()
