import streamlit as st
from helpers import Processor, PlaylistMaker
import asyncio
import os
import urllib.parse

@st.cache_data
def get_playlist_maker(playlist_name, youtube_url):
    return st.session_state.playlist

def set_playlist_maker(playlist):
    st.session_state.playlist= playlist

@st.cache_data
def authenticator(playlist, state_data):
    auth_url = playlist.authenticate(state=state_data) 
    print('authenticating...')
    st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">',  unsafe_allow_html=True)
    return playlist.authenticate()

def main():
    os.environ["PATH"] += os.pathsep + f'/workspaces/youtify'
    if 'playlist' not in st.session_state:
        set_playlist_maker(PlaylistMaker())

    # if  'youtube_url' not in st.session_state:
    #     st.session_state.youtube_url= None
    
    st.title("Youtify 🎵")
    st.write(
        "Convert your favorite YouTube music videos to Spotify playlists!"
    )

    input_form= st.form(key='form', clear_on_submit=True)
    youtube_url = input_form.text_input("Enter the YouTube URL:", key="_youtube_url")
    playlist_name= input_form.text_input("Enter the name of the playlist you want to create on Spotify:", key="_playlist_name")
    button = input_form.form_submit_button('Create my playlist!')
    if button:
        st.session_state.playlist= get_playlist_maker(playlist_name, youtube_url)
        if not st.session_state.playlist.authenticated:
            state_data = f"{youtube_url}|||{playlist_name}"
            auth_url = st.session_state.playlist.get_authenticator(state=state_data) 
            print('authenticating at : ', auth_url)
            try:
                st.link_button('Authenticate here', url= auth_url)
                # st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">',  unsafe_allow_html=True)
            except Exception as e:
                print('Fail to authenticate due to ', str(e))
    # after redirection
    query_params = st.query_params
    if 'code' in query_params and 'state' in query_params:
        with st.spinner('Creating playlist...'):
            st.divider()
            text= st.empty()
            print('creating playlist....') 
            if not st.session_state.playlist.authenticated:
                decoded_state = urllib.parse.unquote(query_params['state'])
                st.session_state.youtube_url, st.session_state.playlist_name = decoded_state.split('|||')
                st.session_state.playlist_name= st.session_state.playlist_name.replace(' ', '+')
                st.session_state.playlist= get_playlist_maker(st.session_state.playlist_name, st.session_state.youtube_url)
                st.session_state.playlist.authenticate(query_params['code'])
                set_playlist_maker(st.session_state.playlist)
            
            else:
                st.session_state.playlist_name= st.session_state._playlist_name
                st.session_state.youtube_url= st.session_state._youtube_url
                st.session_state.playlist= get_playlist_maker(st.session_state.playlist_name, st.session_state.youtube_url)
                
            print('youtube_url: ', st.session_state.youtube_url)
            print('playlist_name: ', st.session_state.playlist_name)
            # st.session_state.playlist= get_playlist_maker()
            st.session_state.playlist.create_playlist(st.session_state.playlist_name)
            print('playlist created!')

            text.write('Retrieving and processing Youtube URL...')
            try: 
                track = Processor(st.session_state.youtube_url)
                print('Processor created')
            except:
                print('Invalid URL')
                text.write('Failed to initialize processor, please refresh page.')
                raise SystemExit

            try:
                text.write('Authenticating youtube...')
                track.process_url()
                print('Youtube URL retrieved and processed')
            except Exception as e:
                print('Failed to process track due to ', str(e))
                text.write('Failed to process track, please refresh page.')
                raise SystemExit

            start_time=0
            video_length= track.video_length()
            track_ids= set()

            while start_time< video_length:
                try:
                    text.write(f"\nFound {len(track_ids)} {'tracks' if len(track_ids)>1 else 'track'}. Recognizing the next track...\n")
                    print('\nRecognizing the next track...\n')
                    isrc, track_title=  track.recognize_audio(start_time=start_time)
                    print("Looking for: ", track_title)
                    track_id, found_title, duration= st.session_state.playlist.lookup(isrc)
                    track_ids.add(track_id)

                    start_time+=duration +5

                except KeyboardInterrupt:
                    print('The [Ctrl+C] key was pressed. Exiting...')
                    raise SystemExit
                
                except Exception as e:
                    print('Track not found')
                    start_time+=60*2.5
            
            if len(track_ids)>0:
                for t in track_ids:
                    st.session_state.playlist.add_to_playlist(t)
                st.success(f'Playlist {st.session_state.playlist_name} created successfully!') 
                st.link_button('View playlist →', st.session_state.playlist.get_playlist()['external_urls']['spotify'])

            else: 
                text.write('0 tracks found. ')
            
            text.empty()



    else:
        st.write('Waiting for authentication...')

if __name__==  "__main__":
    main()

