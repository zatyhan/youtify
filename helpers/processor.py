import requests
from pydub import AudioSegment
import os
import base64
from dotenv import load_dotenv
from pytubefix import YouTube
from pytubefix.cli import on_progress
from io import BytesIO
import json 

class Processor():
    """
    Class to extract audio from youtube video, and recognizing the audio using Shazam API

    """
    def __init__(self, yt_url):
        load_dotenv()
        # shazam api variables
        # self.shazamapi_key = os.getenv('RAPIDAPI_KEY')
        self.shazamapi_key = "20255aac57msh804c236292b3ec2p12abd6jsna3d7d7386a44"
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
    
    def get_audio(self):
        self.buffer.seek(0)  # Make sure to seek to the start of the buffer
        audio = AudioSegment.from_file(self.buffer, format="mp4").split_to_mono()[0]
        audio_data = base64.b64encode(self.buffer.read()).decode('utf-8')
        return audio_data, audio.duration_seconds
    
    
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
            except: 
                print('ISRC not found')
                isrc= None
            
            return isrc, text['track']["title"]
        else:
            raise Exception('Failed to recognize audio')
