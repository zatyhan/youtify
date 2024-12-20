import requests
from pydub import AudioSegment
import os
import base64
# import streamlit as st
from pytubefix import YouTube
from pytubefix.cli import on_progress
from io import BytesIO
import json 
from dotenv import load_dotenv

load_dotenv()

class Processor():
    """
    Class to extract audio from youtube video, and recognizing the audio using Shazam API

    """
    def __init__(self, yt_url):
        # shazam api variables
        self.shazamapi_key = os.getenv('RAPIDAPI_KEY')
        self.shazam_endpoint = "https://shazam.p.rapidapi.com/songs/v2/detect"
        self.querystring = {"timezone":"America/Chicago","locale":"en-US"}
        self.headers = {
            "x-rapidapi-key": self.shazamapi_key,
            "x-rapidapi-host": "shazam.p.rapidapi.com",
            "Content-Type": "text/plain"
        }

        self.yt_url = yt_url
        self.buffer = None

    # def get_token(self):
    #     print('visitor data token: ', st.secrets['VISITOR_DATA'])
    #     print('po token: ', st.secrets['PO_TOKEN'])
    #     def verifier():
    #         return (st.secrets['VISITOR_DATA'], st.secrets['PO_TOKEN'])
    #     return verifier
    
    def process_url(self):
        self.buffer = BytesIO()
        yt= YouTube(self.yt_url, use_oauth=True, allow_oauth_cache=True)       
        # , use_po_token=True, po_token_verifier=self.get_token() 
        yt.streams.filter(only_audio=True).first().stream_to_buffer(self.buffer)

    def video_length(self):
        self.buffer.seek(0)
        audio = AudioSegment.from_file(self.buffer, format="mp4").split_to_mono()[0]

        return audio.duration_seconds
    
    def get_audio(self):
        self.buffer.seek(0)  # Make sure to seek to the start of the buffer
        audio = AudioSegment.from_file(self.buffer, format="mp4").split_to_mono()[0]
        audio_data = base64.b64encode(self.buffer.read()).decode('utf-8')
        return audio_data, audio.duration_seconds
    
    def fingerprint_audio(self, encodedb64, start_time):
        audio_blob = base64.b64decode(encodedb64)
        buffer = BytesIO(audio_blob)
        audio = AudioSegment.from_file(buffer, format="mp4", start_second=start_time, duration=7).split_to_mono()[0]
        audio_data = base64.b64encode(audio._data).decode("utf-8")

        response = requests.request("POST", self.shazam_endpoint, headers=self.headers, data=audio_data, params=self.querystring)

    def recognize_audio(self, start_time=0):
        """
        Recognize audio using Shazam API
        """
        self.buffer.seek(0)
        audio = AudioSegment.from_file(self.buffer, format="mp4", start_second=start_time, duration=7).split_to_mono()[0]
        audio_data = base64.b64encode(audio._data).decode("utf-8")

        response = requests.request("POST", self.shazam_endpoint, headers=self.headers, data=audio_data, params=self.querystring)
        if response.status_code == 200:
            text= response.json()
            try: 
                isrc= text['track']['isrc']
                return isrc, text['track']["title"]
            except: 
                print('ISRC not found')
                return None, None
        else:
            raise Exception('Failed to recognize audio')
