import requests
from pydub import AudioSegment
import os
import base64
from dotenv import load_dotenv
import streamlit as st
from pytubefix import YouTube
from pytubefix.cli import on_progress
from io import BytesIO
import json 


class Processor():
    """
    Class to extract audio from youtube video, and recognizing the audio using Shazam API

    """
    load_dotenv()
    def __init__(self, yt_url):
        # shazam api variables

        # self.shazamapi_key = os.getenv('RAPIDAPI_KEY')
        self.shazamapi_key = st.secrets['RAPIDAPI_KEY']
        # self.shazamapi_key = "20255aac57msh804c236292b3ec2p12abd6jsna3d7d7386a44"
        self.shazam_endpoint = "https://shazam.p.rapidapi.com/songs/v2/detect"
        self.querystring = {"timezone":"America/Chicago","locale":"en-US"}
        self.headers = {
            "x-rapidapi-key": self.shazamapi_key,
            "x-rapidapi-host": "shazam.p.rapidapi.com",
            "Content-Type": "text/plain"
        }

        self.yt_url = yt_url
        self.buffer = None

    def process_url(self):
        self.buffer = BytesIO()
        yt= YouTube(self.yt_url)
        
        yt.streams.filter(only_audio=True).first().stream_to_buffer(self.buffer)

        # return self.buffer

    def video_length(self):
        self.buffer.seek(0)
        audio = AudioSegment.from_file(self.buffer, format="mp4").split_to_mono()[0]

        return audio.duration_seconds
    
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
        # return text['track']["title"], text['track']['subtitle'], text['track']['sections'][0]['metadata'][0]['text']

# pro= Processor("https://www.youtube.com/watch?v=aa8gI5ZVVhs") # nct dream
# pro= Processor("https://www.youtube.com/watch?v=Dd1ILK2EkxI") # nct 127
# track= pro.process_url()
# isrc, track_title= pro.recognize_audio()
# print(track_title, isrc)