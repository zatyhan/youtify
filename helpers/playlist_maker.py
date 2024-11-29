import spotipy
from spotipy.oauth2 import SpotifyOAuth
# import streamlit as st
import os 
from dotenv import load_dotenv

load_dotenv()
class PlaylistMaker():
    def __init__(self, cache_handler):
        self.playlist_name = " "
        self.__scope__='playlist-modify-public'
        self.__clientID__ = os.getenv('SPOTIPY_CLIENT_ID')
        self.__scope__='playlist-modify-public'
        self.__auth_manager__ = SpotifyOAuth(client_id=self.__clientID__, redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'), scope=self.__scope__, cache_handler=cache_handler, show_dialog=True)
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
        print(f"Playlist created: {self.playlist_name} with id {self.playlist_id}")
        return self.playlist_id
    
    def lookup(self, isrc):
        if  isrc:
            query= f"isrc:{isrc}"
            results = self.__sp__.search(query, type="track")
            if results['tracks']['items']:
                track_id= results['tracks']['items'][0]['id']
                duration= results['tracks']['items'][0]['duration_ms']/1000
                return track_id, duration
            else: 
                return None, None
                
    def add_to_playlist(self, track_id, playlist_id):
        # print(self.user_id, playlist_id, track_id)
        try:
            self.__sp__.user_playlist_add_tracks(self.user_id, playlist_id, [track_id])
        except Exception as e:
            print(f"Playlist Maker: Error adding track to playlist: {str(e)}")

    def get_playlist(self, playlist_id):
        return self.__sp__.playlist(playlist_id)['external_urls']['spotify']