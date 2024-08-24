![alt text](/react_app/public/logot4.png)

trading fours is your own personalized Spotify recommendation engine.

- Search for a playlist or song / or browse your own library of saved playlists directly on the site, and T4 will recommend alike tracks based on genre & track attr\ibutes
- Its thinking is influenced by what you have been listening to as of late, and will use that data to tailor the songs it recommends to you
- Behind the scenes, user and song info is being safely handled and stored using MySQL, and the bulk of the recommendations is being done via Python, where playlist / track data is being processed and computed in a ~45 dimensional space against a dataset of over 200,000+ songs (and growing!) to provide the best recommendations.

## Demo:

[![YouTube Video Demo](https://github.com/Stanley-Wang910/spotify-rec-engine/assets/117041405/78ccde6e-b337-481d-92a2-ca0e2c796504)](https://youtu.be/vhLH-nkAxKA?si=VowvksWtWva9jXmC)

## Recent Additions!!

1. Personalized Recommendations by Artist & User
2. Engine Optimization for Faster Recommendation Turnaround
3. Pagination Handling for Spotify API to Grab All Tracks in Playlists > 100 tracks
4. Redis Cloud Session Storage for Higher Memory Limits
5. Smarter diversification of Recommendations, Tailored to the Taste Profile of the User & Playlist

## Features Coming Soon

1. Recommendations for Users and Friends!
2. Recommendation Info Visualization
3. App Hosting

## Contact

    Email: wangstanley910@gmail.com
    School Email: stanley.wang@mail.mcgill.ca
    LinkedIn: https://www.linkedin.com/in/stanley910/

## Data Sources

The initial dataframe of ~200,000 songs was collected and altered from the following:

- [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset)
- [Ultimate Spotify Tracks DB](https://www.kaggle.com/datasets/zaheenhamidani/ultimate-spotify-tracks-db)

However, the dataframe is continually updated by playlists and tracks that users enter!

Logo Notes by: <a href="https://www.freepik.com/free-vector/illustration-set-music-note-icons_2582736.htm#query=music%20note%20svg&position=12&from_view=keyword&track=ais_user&uuid=d09becc7-341a-4a7c-9fac-31370426cbc0">rawpixel.com</a>
