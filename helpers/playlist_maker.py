import spotipy
from spotipy.oauth2 import SpotifyPKCE
from dotenv import load_dotenv
import os

class PlaylistMaker():
    def __init__(self, name):
        load_dotenv()
        self.playlist_name = name
        self.__clientID__ = os.getenv('SPOTIFY_CLIENT_ID')
        self.__scope__='playlist-modify-public'
        self.__auth_manager__ = SpotifyPKCE(client_id=self.__clientID__, redirect_uri="https://youtify.streamlit.app/", scope=self.__scope__)
        self.__sp__ = spotipy.Spotify(auth_manager=self.__auth_manager__)
        self.user_id= self.__sp__.me()['id']
        self.playlist_id = self.__sp__.user_playlist_create(self.user_id, self.playlist_name)['id'] #add template for description later

    def lookup(self, track_name, artist_name, album=None):
        if album is None:
            query= f"q=remaster%20track:{track_name.replace(' ', '%20')}%20artist:{artist_name.replace(' ', '%20')}"
        else:
            query= f"q=remaster%20track:{track_name.replace(' ', '%20')}%20artist:{artist_name.replace(' ', '%20')}%20album:{album.replace(' ', '%20')}"
        # print(query)
        results = self.__sp__.search(query, type="track")
        track_id= results['tracks']['items'][0]['id']
        duration= results['tracks']['items'][0]['duration_ms']/1000
        track_title= results['tracks']['items'][0]['name']
        return track_id, track_title, duration

    def add_to_playlist(self, track_id):
        self.__sp__.user_playlist_add_tracks(self.user_id, self.playlist_id, [track_id])
        # print(self.__sp__.user_playlist_tracks(self.user_id, self.playlist_id))

# pm= PlaylistMaker('test 2')
# track_id,  duration = pm.lookup('Supernatural', 'NewJeans')
# pm.add_to_playlist(track_id)
# track_id,  duration = pm.lookup('Berharap Kau Kembali', 'Fabio Asher')
# pm.add_to_playlist(track_id)
