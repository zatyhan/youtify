import streamlit as st
from helpers import Processor, PlaylistMaker
import asyncio
import urllib.parse

    
@st.cache_data
def get_playlist_maker():
    return st.session_state.playlist

def set_playlist_maker(playlist):
    st.session_state.playlist= playlist

def sign_in(state):
    try: 
        # auth_url= st.session_state.playlist.get_auth_url(state)
        auth_url= 'https://www.google.com/'
        link_html = " <a href=\"{url}\" >{msg}</a> ".format(
        url=auth_url,
        msg="Click me to authenticate!")
        st.html(link_html)
    except Exception as e: 
        st.write(f'Error during authorization: {str(e)}')
    
    else: 
        st.success('redirecting to Spotify for authentication...')
        # st.session_state.signed_in= True
        # st.success('Successfully authenticated!')


st.title("Youtify Refactor ver🎵")
st.write(
    "Convert your favorite YouTube music videos to Spotify playlists!"
)

if 'playlist' not in st.session_state:
   set_playlist_maker(PlaylistMaker())

if 'signed_in' not in st.session_state:
    st.session_state.signed_in = False

if 'code'  not in st.session_state:
    st.session_state.code= ""

if 'youtube_url' not in st.session_state: 
    st.session_state.youtube_url= None

if 'playlist_name' not in st.session_state:
    st.session_state.playlist_name= None

input_form= st.form(key='form', clear_on_submit=True)
youtube_url = input_form.text_input("Enter the YouTube URL:", key="_youtube_url")
playlist_name= input_form.text_input("Enter the name of the playlist you want to create on Spotify:", key="_playlist_name")
button = input_form.form_submit_button('Create my playlist!')

if button:
    # so that user only need to do this once
    st.session_state.youtube_url= youtube_url
    st.session_state.playlist_name= playlist_name

    if not st.session_state.signed_in:
        st.session_state.playlist= get_playlist_maker()
        state_data = f"{youtube_url}|||{playlist_name}"
        sign_in(state_data)
        set_playlist_maker(st.session_state.playlist)
    #check if yotuuber url and playlist name is preserved across redirects

print('youtube_url out: ', st.session_state.youtube_url)
print('playlist_name out: ', st.session_state.playlist_name)
query_params = st.query_params
if 'code' in query_params and 'state' in query_params:
    if not st.session_state.youtube_url and not st.session_state.playlist_name:
        decoded_state = urllib.parse.unquote(query_params['state'])
        st.session_state.youtube_url, st.session_state.playlist_name= decoded_state.split('|||')
   
    text= st.empty()
    print('creating playlist....')
    st.session_state.code= query_params['code']

    # only need to sign in once
    if not st.session_state.signed_in:
        try: 
            st.session_state.playlist_maker= get_playlist_maker()
            st.session_state.playlist_maker.authorize(st.session_state.code)
        
        except Exception as e:
            st.write(f'Error during authorization: {str(e)}')
        
        else:
            text.success('Successfully authenticated!')
            st.session_state.signed_in= True
            set_playlist_maker(st.session_state.playlist_maker)
    
    print('youtube_url: ', st.session_state.youtube_url)
    print('playlist_name: ', st.session_state.playlist_name)
    
    try:
        st.session_state.playlist_maker.create_playlist(st.session_state.playlist_name)
    except Exception as e:
        st.write(f'Error during playlist creation: {str(e)}')
    else:
        text.success('Playlist created successfully!')
    
        text.write('Retrieving and processing Youtube URL...')
    
        try: 
            track = Processor(st.session_state.youtube_url)
            print('Processor created')

        except Exception as e:
            text.write('ERROR: Failed to create processor:', str(e))

        else:
            text.success('Processor created successfully')
            try:
                track.process_url()
                print('Youtube URL retrieved and processed')
            except Exception as e:
                print('Failed to process track due to ', str(e))
                text.write('Failed to process track, please refresh page.')

            else:
                start_time=0
                video_length= track.video_length()
                track_ids= set()

                while start_time< video_length:
                    try:
                        text.write(f"\nFound {len(track_ids)} {'tracks' if len(track_ids)>1 else 'track'}. Recognizing the next track...\n")
                        print('\nRecognizing the next track...\n')
                        isrc, track_title=  track.recognize_audio(start_time=start_time)
                        print("Looking for: ", track_title)
                        # text.write(f"Looking for: {track_title}")
                        track_id, found_title, duration= st.session_state.playlist.lookup(isrc)
                        # text.write(f"Found: {found_title}")
                        track_ids.add(track_id)

                        start_time+=duration +5

                    except KeyboardInterrupt:
                        print('The [Ctrl+C] key was pressed. Exiting...')
                        raise SystemExit
                    
                    except Exception as e:
                        print('Track not found ')
                        start_time+=60*2.5
                        
                for t in track_ids:
                    st.session_state.playlist.add_to_playlist(t)
                text.empty()

                st.success(f'Playlist {st.session_state.playlist_name} created successfully!') 

                st.link_button('View playlist →', st.session_state.playlist.get_playlist()['external_urls']['spotify'])









