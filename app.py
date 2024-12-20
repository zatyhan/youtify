from flask import Flask, render_template, url_for, request, redirect, session, jsonify
from flask_session import Session
import redis 
from flask_cors import CORS
# from flask_caching import Cache
import urllib.parse

# miscellaneous, system modules 
from helpers import PlaylistMaker 
import requests
from io import BytesIO
import os 

# modules for youtube audio extraction
from dotenv import load_dotenv
from pytubefix import YouTube
from pydub import AudioSegment
import base64

# modules for spotify api 
import spotipy

app = Flask(__name__)
app.config.from_object('config.BaseConfig')

redis_host= os.getenv('REDISHOST', 'localhost')
redis_port = int(os.getenv('REDISPORT', 6379))

# if set to localhost, can run on local machine with the redis server running on docker 
redis_db = redis.Redis(host=redis_host, port=redis_port) 

load_dotenv()

# configuring redis
#  connect to tcp socket via redis://
app.config['SESSION_REDIS'] = redis_db

app.config['DEBUG'] = os.getenv('FLASK_DEBUG')
Session(app)
CORS(app)

app.secret_key= os.getenv('SECRET_KEY') 

@app.route('/', methods=['GET','POST'])
def index():
    cache_handler= spotipy.cache_handler.RedisCacheHandler(redis=redis_db, key=os.getenv('REDISAPI_KEY'))
    sp= PlaylistMaker(cache_handler=cache_handler)

    if sp.validate_token(cache_handler.get_cached_token()):
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        try:
            return redirect(sp.get_auth_url())
        except Exception as e:
            print(f'Error during authorization: {str(e)}')
            return render_template('index.html', auth_status='Error') 
        
    return render_template('index.html')           


@app.route('/home', methods=['GET','POST'])
def home():

    cache_handler= spotipy.cache_handler.RedisCacheHandler(redis=redis_db, key=os.getenv('REDISAPI_KEY'))
    sp = PlaylistMaker(cache_handler=cache_handler)
    
    try:
        sp.authorize(session['code'])
    except Exception as e:
        return redirect(sp.get_auth_url())

    return render_template('home.html')

@app.route('/create-playlist', methods=['POST'])
def create_playlist():
    request_data= request.get_json()
    name= urllib.parse.unquote(request_data)
    cache_handler= spotipy.cache_handler.RedisCacheHandler(redis=redis_db, key=os.getenv('REDISAPI_KEY'))
    sp = PlaylistMaker(cache_handler=cache_handler)
    try:
        sp.authorize(session['code'])
    except Exception as e:
        print(str(e))
    else:
        try:
            playlist_id= sp.create_playlist(name)
            return jsonify({'result': 'Playlist created successfully', 'playlist_id': playlist_id}), 200
        except Exception as e:
            print('Failed to create playlist due to error: ', str(e))
            return jsonify({'Error': str(e)})   

@app.route('/process-yt-url', methods=['POST'])
def process_url():
    request_data = request.get_json()
    url = urllib.parse.unquote(request_data)
    buffer = BytesIO()

    try: 
        yt= YouTube(url)
    except Exception as e:
        return jsonify({'Error': 'Failed to process URL due to error: ' + str(e)}), 500
    else:
        try:
            yt.streams.filter(only_audio=True).first().stream_to_buffer(buffer)
            duration= yt.length
            buffer.seek(0)
            print('Youtube URL retrieved and processed')
            
            return jsonify({'result': 'Youtube URL retrieved and processed',
                            'audio_data': base64.b64encode(buffer.read()).decode('utf-8'),
                            'audio_duration': duration}), 200

        except Exception as e:
            print('Failed to process track due to ', str(e))
            return jsonify({'result': 'Failed to process track due to '+ str(e)}), 500
    

@app.route('/recognize-track', methods=['POST'])
def recognize_track():
    try:
        request_data = request.get_json()
        audio_blob= base64.b64decode(request_data['audio'])
        start_time= request_data['start_time']
        buffer= BytesIO(audio_blob)
        buffer.seek(0)
        shazamapi_key = os.getenv('RAPIDAPI_KEY')
        shazam_endpoint = "https://shazam.p.rapidapi.com/songs/v2/detect"
        querystring = {"timezone":"America/Chicago","locale":"en-US"}
        headers = {
            "x-rapidapi-key": shazamapi_key,
            "x-rapidapi-host": "shazam.p.rapidapi.com",
            "Content-Type": "text/plain"
        }
        audio = AudioSegment.from_file(buffer, format="mp4", start_second=start_time, duration=7).split_to_mono()[0]
        audio_data = base64.b64encode(audio._data).decode('utf-8')
        
        response = requests.request("POST", shazam_endpoint, headers= headers, data=audio_data, params=querystring)
        if response.status_code == 200:
            text= response.json()
            if 'track' in text and 'isrc' in text['track']: 
                return jsonify({'isrc':text['track']['isrc'], 'title':text['track']['title']}), 200
            print(response.text)
            return jsonify({'error': 'Failed to recognize audio'}), 500
        else:
            print(response.text)
            return jsonify({'error': 'Error: '+ str(response.status_code)}), 500
    except Exception as e:
        print('Failed to recognize audio due to error: ', str(e))
        return jsonify({'error': 'Failed to recognize audio due to error: ' + str(e)}), 500
        
@app.route('/add-to-playlist', methods=['POST'])
def add_to_playlist(): 
    request_data = request.get_json()
    isrc= request_data['isrc']
    playlist_id= request_data['playlist_id']
    print('isrc: ', isrc)
    
    cache_handler= spotipy.cache_handler.RedisCacheHandler(redis=redis_db, key=os.getenv('REDISAPI_KEY'))
    sp = PlaylistMaker(cache_handler=cache_handler)

    try:
        sp.authorize(session['code'])
    except Exception as e:
        print('Authorization error: ', str(e))
        return jsonify({'result': 'Authorization error: ' + str(e), 'track_id': None, 'duration': 60*2.5}), 500
    else:
        track_id, duration= sp.lookup(isrc)

        if track_id: 
            sp.add_to_playlist(track_id, playlist_id)
            return jsonify({'result': 'Track added to playlist', 'track_id': track_id, 'duration': duration}), 200
        else:
            return jsonify({'result': 'Track not found by spotify', 'track_id': None, 'duration': 60*2.5}), 200
    try:
        sp.add_to_playlist(track_id, playlist_id)
    except Exception as e:
        print(f"Error adding track to playlist: {str(e)}")
        return jsonify({'result': 'Error adding track to playlist: ' + str(e), 'track_id': track_id, 'duration': duration}), 500
    else:
        return jsonify({'result': 'Track added to playlist', 'track_id': track_id, 'duration': duration}), 200

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return redirect(url_for('index'))
        return jsonify({'error': request.args['error']}), 400

    if 'code' in request.args: 
        session['code']= request.args['code']
        return redirect(url_for('home'))

@app.route('/get-playlist-url', methods=['POST'])
def get_playlist_url():
    request_data = request.get_json()
    playlist_id = request_data['playlist_id']
    
    cache_handler= spotipy.cache_handler.RedisCacheHandler(redis=redis_db, key=os.getenv('REDISAPI_KEY'))
    sp = PlaylistMaker(cache_handler=cache_handler)
    try:
        sp.authorize(session['code'])
    except Exception as e:
        print('Authorization error: ', str(e))
        return jsonify({'result': 'Authorization error: ' + str(e), 'playlist_url': None}), 500
    else:
        playlist_url = sp.get_playlist(playlist_id) 
        return jsonify({'playlist_url': playlist_url}), 200

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(port=os.getenv('PORT', '8080'))
