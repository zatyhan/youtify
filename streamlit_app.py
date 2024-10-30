import streamlit as st
from helpers import Processor, PlaylistMaker
import webbrowser


def redirect(url):
    js = f'window.open("{url}", "_self");'
    st.components.v1.html(f'<script>{js}</script>', height=0)
    
st.title("Youtify 🎵")
st.write(
    "Convert your favorite YouTube music videos to Spotify playlists!"
)

input_form= st.form(key='form', clear_on_submit=True)
# Get the YouTube URL from the user
youtube_url = input_form.text_input("Enter the YouTube URL:", key="youtube_url", value= "https://www.youtube.com/watch?v=rMZeKQYLXWc")

# Get the name of the playlist from the user
playlist_name= input_form.text_input("Enter the name of the playlist you want to create on Spotify:", key="playlist_name", value= "My Playlist")

button = input_form.form_submit_button('Create my playlist!')

if button:
    st.session_state.playlist= PlaylistMaker(st.session_state.playlist_name)
    if 'sp' not in st.session_state:
        auth_url = st.session_state.playlist.authenticate()
        # print(auth_url)
        # webbrowser.open(url=st.session_state.auth_url)
        st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">',  unsafe_allow_html=True)
        # redirect(auth_url)
        # query_params= st.query_params()
        # print(query_params)
        # st.write(st.query_params)   
        # print('here')

    else: 
        sp= st.session_state.sp
        user_info = sp.me()
        st.write(f"Hello {user_info['display_name']}!")

if 'code' in st.query_params:
    code = st.query_params['code'][0]
    st.session_state.playlist.create_playlist(code)
    st.write('Successfully created playlist')

else: 
    st.write('Did not pass authentication')
    raise SystemExit



