from flask import Flask, render_template, url_for, request, redirect, session
from helpers import Processor, PlaylistMaker 
from dotenv import load_dotenv
from flask_session import Session
import os 
import jsonify
import json 
import spotipy
from spotipy.oauth2 import SpotifyPKCE


app = Flask(__name__)

load_dotenv()
app.secret_key= os.getenv('SECRET_KEY') 
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)


@app.route('/', methods=['GET','POST'])
def index():

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    sp= PlaylistMaker(cache_handler=cache_handler)

    if request.method == 'POST':
        session['yt_url'] = request.form['youtube-url']
        session['playlist_name'] = request.form['playlist-name']

        if sp.authorized==False:
            try:
                sp= PlaylistMaker(cache_handler=cache_handler)
                return redirect(sp.get_auth_url())
            except Exception as e:
                print(f'Error during authorization: {str(e)}')
                return render_template('index.html', auth_status='Error')

        else:
            return redirect(url_for('home'))

    else:   
        return render_template('index.html')

@app.route('/home', methods=['GET','POST'])
def home():

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    sp = PlaylistMaker(cache_handler=cache_handler)
    sp.authorize(session['code'])

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
                        print('Track not found ')
                        start_time+=60*2.5
                
                for t in track_ids:
                    sp.add_to_playlist(t)
                
                playlist_url= sp.get_playlist()['external_urls']['spotify']
                return render_template('index.html', auth_status='Authenticated', playlist_url=playlist_url)

    return render_template('index.html', auth_status='Error')
    


@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({'error': request.args['error']}), 400

    if 'code' in request.args: 
        session['code']= request.args['code']
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)