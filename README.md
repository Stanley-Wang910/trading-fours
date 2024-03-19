# Spotify Recommendation Engine

## Description

This project is a robust Spotify Recommendation Engine that takes a playlist or a track as input. It uses a random forest classification model to predict overarching track or playlist genre. This model was trained on over 200,000 songs and 20 genres. The recommendation engine then utilizes the spotipy library and the Spotify Web API to retrieve individual track attributes, and creates a vector representative of the playlist/track within a ~45 dimensional space. This vector is compared against an immense dataset of diverse songs in both genre and audio features and is then assigned a cosine similarity, which is finally used to determine the best recommendations for the given playlist/track.

## Example Usage & Analysis
Here is a demonstrated example on one of my own playlists. To stress test my recommendation engine, I fed it a playlist of mine that I had created for the month of December (with no specific genre in mind).
This way, I would be able to see how versatile its recommendations would be when given an equally diverse playlist:

<img src="https://github.com/Stanley-Wang910/spotify-rec-engine/assets/117041405/797d8981-9d90-4b7f-b3d0-5c522fcc3509" width="600" /><br>
Link: https://open.spotify.com/playlist/66ehpqp3UGSK8e9tglfYw7?si=63b02de8d6a0430f<br>

<img src="https://github.com/Stanley-Wang910/spotify-rec-engine/assets/117041405/14ca562b-2eea-4eb5-8dfd-3014bf0a9847" width="600" /><br>
Spotify's Official Recommendations<br>

<img src="https://github.com/Stanley-Wang910/spotify-rec-engine/assets/117041405/474dfd07-18a4-47a6-a329-1194eb9c3a90" width="1000" /><br>
My Engine's first pick recommendations

Analysis:<br>
Similarities in Artist recommendations: 
See Blood Orange: '[Charcoal Baby](https://www.youtube.com/watch?v=hIlauccaH88)' from Spotify, '[Augustine](https://www.youtube.com/watch?v=NXtzcViZPGA)' from my engine.<br> 

Understanding of Playlist Sound & Vibe:
However, beyond just being accurate to Spotify's own recommendations, we can see that my engine also has an understanding of the sound & vibe of the entire playlist: The top recommendation by my engine is '[Father And Son](https://www.youtube.com/watch?v=KicjYWFdCNY)' by Yusuf / Cat Stevens, a beautiful track backed by stripped acoustic guitars, a raw lead vocal performance, and pockets between verses where the instrumental sings. The very first song on my playlist is '[If](https://www.youtube.com/watch?v=e7t7aQLcik0)' by Pink Floyd, which shares a similarly stripped back guitar, a very intimate delivery on behalf of Roger Waters, and musical solo sections within the track. Furthermore, my engine recommends '[MICHIGAN](https://www.youtube.com/watch?v=R8894AYaRcU)' by Brockhampton. One of their frontmen is Kevin Abstract, whose song '[The Greys](https://www.youtube.com/watch?v=i7OGxY_EV7M)' is the most recent addition to the playlist.

## Features Coming Soon

1. Stylized Front End Integration (Flask, React)
2. User authorization flow directly handled through Web Spotify API so that anybody with a Spotify Account can try getting recommendations
3. Diverse handling of new custom datasets to recommend songs, pulled from the unique playlists that Spotify's curates for the user, enabling even more accurate recommendations

## Contact

    Email: wangstanley910@gmail.com
    School Email: stanley.wang@mail.mcgill.ca
    LinkedIn: https://www.linkedin.com/in/stanley910/

## Installation

To install and run this project, follow these steps:

1. Clone the repository to your local machine:
    ```
    git clone https://github.com/Stanley-Wang910/spotify-rec-engine.git
    ```

2. Navigate to the project directory:
    ```
    cd <path to your project directory>
    ```

3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

To use this Spotify Recommendation Engine, follow these steps:

1. Create a Spotify Developer Account:
    - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and log in or create a new account.
    - Create a new app and note down the Client ID and Client Secret.

2. Set up the Redirect URI:
    - In the Spotify Developer Dashboard, go to your app settings.
    - Add a Redirect URI for your application. This should be the URL where the user will be redirected after authentication. For example, `http://localhost:8000/callback`.

3. Create a `.env` file in the root directory of your project:
    - Open a text editor and create a new file named `.env`.
    - Add the following lines to the `.env` file, replacing `<YOUR_CLIENT_ID>`, `<YOUR_CLIENT_SECRET>`, and `YOUR_USER_ID` with your actual Client ID, Client Secret, and User ID:
      ```
      CLIENT_ID=<YOUR_CLIENT_ID>
      CLIENT_SECRET=<YOUR_CLIENT_SECRET>
      SPOTIFY_USER_ID=<YOUR_USER_ID>
      REDIRECT_URI=http://localhost:8000/callback
      ```

4. Run the program!
    - in terminal:
      ```
      <User Directory>\RecEngine> python .\src\main.py
      ```
    - Have fun!

## Data Sources

This project uses altered and combined data from the following sources:

- [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset)
- [Ultimate Spotify Tracks DB](https://www.kaggle.com/datasets/zaheenhamidani/ultimate-spotify-tracks-db)





