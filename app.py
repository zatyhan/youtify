from flask import Flask, render_template, url_for, request, redirect, session, jsonify
from helpers import Processor, PlaylistMaker 
from dotenv import load_dotenv
from flask_session import Session
import os 
# import jsonify
import json 
import spotipy
from flask_cors import CORS
import urllib.parse

app = Flask(__name__)

load_dotenv()
app.secret_key= os.getenv('SECRET_KEY') 
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)
CORS(app)


@app.route('/', methods=['GET','POST'])
def index():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
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

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    sp = PlaylistMaker(cache_handler=cache_handler)
    
    try:
        sp.authorize(session['code'])
        print('authorized')
    except Exception as e:
        return redirect(sp.get_auth_url())

    return render_template('home.html')

@app.route('/create-playlist', methods=['POST'])
def create_playlist():
    request_data= request.get_json()
    # print(request_data)
    name= urllib.parse.unquote(request_data)
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    sp = PlaylistMaker(cache_handler=cache_handler)
    try:
        sp.authorize(session['code'])
        print('authorized')
    except Exception as e:
        print(str(e))
    else:
        try:
            sp.create_playlist(name)
            return jsonify({'result': 'Playlist created successfully'})
        except Exception as e:
            print('Failed to create playlist due to error: ', str(e))
            return jsonify({'Error': str(e)})   

@app.route('/process-yt-url', methods=['POST'])
def process_url():
    request_data = request.get_json()
    url = urllib.parse.unquote(request_data)

    try:
        tracks = Processor(url)

    except Exception as e:
        print('Failed to retrieve audio from youtube video due to error: ', str(e))
        return jsonify({'Error': str(e)})
    else: 

        try: 
            tracks.process_url()
            print('Youtube URL retrieved and processed')
            audio_data, duration= tracks.get_audio()
            return jsonify({'result': 'Youtube URL retrieved and processed',
                            'audio_b64_data': audio_data,
                            'audio_duration': duration})

        except Exception as e:
            print('Failed to process track due to ', str(e))
            return jsonify({'Error': str(e)})
    

@app.route('/recognize-tracks', methods=['POST'])
def recognize_tracks():
    start_time=0
    video_length= tracks.video_length()
    track_ids= set()

    while start_time< video_length:
        try:
            print(f"\nFound {len(track_ids)} {'tracks' if len(track_ids)>1 else 'track'}. Recognizing the next track...\n")
            print('\nRecognizing the next track...\n')
            isrc, track_title=  tracks.recognize_audio(start_time=start_time)
            print("Looking for: ", track_title)
            track_id, found_title, duration= sp.lookup(isrc)
            track_ids.add(track_id)

            start_time+=duration +5

        except KeyboardInterrupt:
            print('The [Ctrl+C] key was pressed. Exiting...')
            raise SystemExit
        
        except Exception as e:
            print('Track not found due to error: ', str(e))
            start_time+=60*2.5

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({'error': request.args['error']}), 400

    if 'code' in request.args: 
        session['code']= request.args['code']
        return redirect(url_for('home'))

@app.route('/recognise')
def recognise():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    sp = PlaylistMaker(cache_handler=cache_handler)

    try:
        sp.create_playlist(session['playlist_name'])
        print('Playlist created successfully')
    except Exception as e:
        print('Failed to create playlist due to error: ', str(e))
        session.clear()
        return render_template('index.html', auth_status='Failed to create playlist. Please enter the details again.')
    else:
        print('Retrieving audio from youtube video...')

        try:
            tracks = Processor(session['yt_url'])

        except Exception as e:
            print('Failed to retrieve audio from youtube video due to error: ', str(e))

        else: 
            try: 
                tracks.process_url()
                print('Youtube URL retrieved and processed')
            except Exception as e:
                print('Failed to process track due to ', str(e))
                raise SystemExit
            else:
                start_time=0
                video_length= tracks.video_length()
                track_ids= set()

                while start_time< video_length:
                    try:
                        print(f"\nFound {len(track_ids)} {'tracks' if len(track_ids)>1 else 'track'}. Recognizing the next track...\n")
                        print('\nRecognizing the next track...\n')
                        isrc, track_title=  tracks.recognize_audio(start_time=start_time)
                        print("Looking for: ", track_title)
                        track_id, found_title, duration= sp.lookup(isrc)
                        track_ids.add(track_id)

                        start_time+=duration +5

                    except KeyboardInterrupt:
                        print('The [Ctrl+C] key was pressed. Exiting...')
                        raise SystemExit
                    
                    except Exception as e:
                        print('Track not found due to error: ', str(e))
                        start_time+=60*2.5
                
                for t in track_ids:
                    sp.add_to_playlist(t)
                
                playlist_url= sp.get_playlist()['external_urls']['spotify']
                return render_template('home.html', auth_status='Authenticated', playlist_url=playlist_url)

    return 'text'

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, threaded=True, port=int(os.environ.get("PORT", os.environ.get("SPOTIPY_REDIRECT_URI", 8080).split(":")[-1])))
