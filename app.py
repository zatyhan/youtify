from flask import Flask, render_template, url_for, request, redirect, session
from flask_dance.contrib.spotify import make_spotify_blueprint, spotify
from helpers import Processor, PlaylistMaker 
from dotenv import load_dotenv
import os 
import jsonify 

app = Flask(__name__)

load_dotenv()
app.secret_key= os.getenv('SECRET_KEY') 
# print(app.secret_key)
# redirect_url= "https://youtify.streamlit.app"
# redirect_uri= "http://127.0.0.1:5000/callback"
# spotify_blueprint= make_spotify_blueprint(client_id=os.getenv('SPOTIFY_CLIENT_ID'), client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'), redirect_url=redirect_url, scope='playlist-modify-public')

# app.register_blueprint(spotify_blueprint, url_prefix='/spotify_login')

@app.route('/', methods=['GET','POST'])
def home():

    if 'code' in session:
        try:
            sp.create_playlist(session['playlist_name'])
            print('Playlist created successfully')
        except Exception as e:
            print('Failed to create playlist')
            raise SystemExit
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
    if request.method == 'POST':
        session['yt_url'] = request.form['youtube-url']
        session['playlist_name'] = request.form['playlist-name']
        
        try:
            sp= PlaylistMaker()
            return redirect(sp.get_auth_url())
        except Exception as e:
            print(f'Error during authorization: {str(e)}')
        #  if not spotify.authorized:
        #     return redirect(url_for('spotify.login'))

    else:   
        return render_template('index.html')

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({'error': request.args['error']}), 400

    if 'code' in request.args: 
        session['code']= request.args['code']
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)