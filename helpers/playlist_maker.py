import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import os 
from dotenv import load_dotenv
load_dotenv()

class PlaylistMaker():
    def __init__(self, cache_handler):
        self.playlist_name = " "
        self.__scope__='playlist-modify-public'
        self.__clientID__ = os.getenv('SPOTIPY_CLIENT_ID')
        self.__scope__='playlist-modify-public'
        self.redirect_uri= os.getenv('SPOTIPY_REDIRECT_URI')
        self.__auth_manager__ = SpotifyOAuth(client_id=self.__clientID__, redirect_uri="http://127.0.0.1:5000/callback", scope=self.__scope__, cache_handler=cache_handler, show_dialog=True)
        self.user_id= None
        self.__sp__= None
        self.playlist_id= None
    def get_auth_url(self, state=None):
        url= self.__auth_manager__.get_authorize_url(state=state)
        return url        

    def validate_token(self, token):
        return self.__auth_manager__.validate_token(token)
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