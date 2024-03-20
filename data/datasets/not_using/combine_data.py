# import pandas as pd

# df = pd.read_csv('data/unique_tracks.csv')
# 89743
# df = pd.read_csv('data/dataset.csv')
# key_mapping = {
#     'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
#     'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
# }
# mode_mapping = { 'Major' : 1, 'Minor' : 0}
# df = pd.read_csv('data/combined_genres.csv')
# time_mapping = { 4 : '4', 3 : '3', 2 : '2', 5 : '5', 1 : '1'}
# df['time_signature'] = df['time_signature'].map(time_mapping)
# df.to_csv('data/combined_genres.csv', index=False)
# df['key'] = df['key'].map(key_mapping)
# df['mode'] = df['mode'].map(mode_mapping)

# if df['key'].isnull().any():
#     print("There are unmapped key values in the 'key' column.")
    
# if df['mode'].isnull().any():
#     print("There are unmapped key values in the 'key' column.")

# df.to_csv('data/dataset1.csv', index=False)

# df = pd.read_csv('data/unique_tracks.csv')

# filter_df =df[~df['track_genre'].isin(["Comedy", "Children's Music", "children", "Children’s Music", "comedy", "showtunes", "kids", "sleep", "disney", "study", "ambient", "new-age", "happy","Ska", "A capella", "ska", "british", "world-music", "brazil", "spanish", "iranian", "malay", "dancehall", "forro", "afrobeat", "pop-film"])]
# filter_df.to_csv('data/seperate_genres.csv', index=False)
# genre_counts = filter_df['track_genre'].value_counts()
# genre_counts.to_csv('data/genre_counts.csv', index=True, header=['count'])


# ######### Combine Datasets Logic
# ###loudness(flaot) energy(float) tempo(float)
# df1 = pd.read_csv('data/dataset.csv')
# df2 = pd.read_csv('data/SpotifyFeatures.csv')
# columns_order = ['artists', 'track_name', 'track_id', 'popularity', 'duration_ms', 'danceability', 'energy', 'key', 
#                         'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 
#                         'liveness', 'valence', 'tempo', 'time_signature', 'track_genre']

# df2.rename(columns={'genre': 'track_genre', 'artist_name': 'artists'}, inplace=True)
# df_concatenated = pd.concat([df1, df2], ignore_index=True)
# df_unique = df_concatenated.drop_duplicates(subset='track_id', keep='first')
# df_unique = df_unique.reindex(columns=columns_order)
# df_unique.reset_index(drop=True, inplace=True)
# df_unique.to_csv('data/unique_tracks1.csv', index=False)

# ########

# # Combine Genre Logic
# df = pd.read_csv('data/combined_genres.csv')
# filter_df = df[~df['track_genre'].isin(["show-tunes", "A Capella"])]
# filter_df.to_csv('data/combined_genres.csv', index=False)

# genre_mapping = {
#     'j-rock': 'Anime', 'j-dance': 'Anime', 'j-idol': 'Anime', 'anime': 'Anime',
#     'house': 'Electronic', 'dubstep': 'Electronic', 'tecno': 'Electronic', 'edm': 'Electronic',
#     'trance': 'Electronic', 'electro': 'Electronic', 'progressive-house': 'Electronic', 'party': 'Electronic',
#     'minimal-techno': 'Electronic', 'hardstyle': 'Electronic', 'garage': 'Electronic', 'dub': 'Electronic',
#     'detroit-techno': 'Electronic', 'deep-house': 'Electronic', 'idm': 'Electronic', 'breakbeat': 'Electronic', 'chicago-house': 'Electronic',
#     'piano': 'Classical', 'classical': 'Classical',
#     'reggae': 'Reggae',
#     'reggaeton': 'Reggaeton',
#     'blues': 'Blues', 'bluegrass': 'Blues',
#     'opera': 'Opera',
#     'alternative': 'Alternative', 'industrial': 'Alternative', 'alt-rock': 'Alternative',
#     'jazz': 'Jazz',
#     'latino': 'World', 'samba': 'World','german': 'World','indian': 'World','latin': 'World','swedish': 'World','mpb': 'World','sertanejo': 'World','pagode': 'World','turkish': 'World','french': 'World',
#     'folk': 'Folk',
#     'groove': 'Dance', 'disco': 'Dance', 'dance': 'Dance', 'salsa': 'Dance', 'club': 'Dance', 'tango': 'Dance',
#     'country': 'Country', 'honky-tonk': 'Country',
#     'hip-hop': 'Hip-Hop', 'trip-hop': 'Hip-Hop', 'rap': 'Hip-Hop',
#     'r-n-b': 'R&B', 'funk': 'R&B', 'chill': 'R&B',
#     'soul': 'Soul', 'gospel': 'Soul',
#     'indie': 'Indie', 'singer-songwriter': 'Indie', 'sad': 'Indie', 'romance': 'Indie', 'emo': 'Indie', 'acoustic': 'Indie',
#     'pop': 'Pop', 'indie-pop': 'Pop', 'j-pop': 'Pop', 'synth-pop': 'Pop', 'mandopop': 'Pop', 'power-pop': 'Pop', 'k-pop': 'Pop', 'canto-pop': 'Pop',
#     'punk': 'Rock', 'metal': 'Rock', 'rock': 'Rock', 'psych-rock': 'Rock', 'rockabilly': 'Rock', 'punk-rock': 'Rock', 'hard-rock': 'Rock', 'metalcore': 'Rock', 'hardcore': 'Rock', 'rock-n-roll': 'Rock', 'grunge': 'Rock', 'guitar': 'Rock', 'death-metal': 'Rock', 'goth': 'Rock', 'drum-and-bass': 'Rock', 'grindcore': 'Rock', 'black-metal': 'Rock', 'heavy-metal': 'Rock',
#     'electronic': 'Electronic', 'techno': 'Electronic', 'cantopop': 'Pop'
# }   

# genre_mapping = {
#     'Movie' : 'Soundtrack', 'Rap' : 'Hip-Hop'
# }
# df['track_genre'] = df['track_genre'].replace(genre_mapping)
# df.to_csv('data/combined_genres.csv', index=False)

# genre_counts = df['track_genre'].value_counts()
# genre_counts.to_csv('data/genre_counts.csv', index=True, header=['count'])

# #### ohe_genre Logic

# df = pd.get_dummies(df, columns=['track_genre'])
# for column in df.columns:
#     if 'track_genre_' in column:
#         df[column] = df[column].astype(int)
# df.to_csv('data/rec_engine_df.csv', index=False)