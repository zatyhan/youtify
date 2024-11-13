import spotipy
from spotipy.oauth2 import SpotifyPKCE
import streamlit as st

class PlaylistMaker():
    def __init__(self):
        self.playlist_name = " "
        self.__scope__='playlist-modify-public'
        self.__clientID__ = st.secrets['SPOTIFY_CLIENT_ID']
        self.__scope__='playlist-modify-public'
        self.redirect_uri= "https://organic-meme-7xpj5v76pjr3xq9j-8501.app.github.dev"
        self.__auth_manager__ = SpotifyPKCE(client_id=self.__clientID__, redirect_uri=self.redirect_uri, scope=self.__scope__)
        # https://organic-meme-7xpj5v76pjr3xq9j-8501.app.github.dev
        # http://localhost:8501
    def get_auth_url(self, state=None):
        url= self.__auth_manager__.get_authorize_url(state=state)
        return url        

    def authorize(self, code):
        self.__auth_manager__.get_access_token(code)
        self.__sp__ = spotipy.Spotify(auth_manager=self.__auth_manager__)
        self.user_id= self.__sp__.me()['id']

    def create_playlist(self, name):
        self.playlist_name= name
        self.playlist_id = self.__sp__.user_playlist_create(self.user_id, self.playlist_name)['id'] #add template for description later
        
    def lookup(self, isrc):
        if  isrc:
            query= f"isrc:{isrc}"
            results = self.__sp__.search(query, type="track")
            track_id= results['tracks']['items'][0]['id']
            duration= results['tracks']['items'][0]['duration_ms']/1000
            track_title= results['tracks']['items'][0]['name']
            return track_id, track_title, duration

    def add_to_playlist(self, track_id):
        self.__sp__.user_playlist_add_tracks(self.user_id, self.playlist_id, [track_id])

    def get_playlist(self):
        return self.__sp__.playlist(self.playlist_id)