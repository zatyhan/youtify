import streamlit as st
from helpers import Processor, PlaylistMaker
import webbrowser

st.title("Youtify 🎵")
st.write(
    "Convert your favorite YouTube music videos to Spotify playlists!"
)

with st.form(key='form', clear_on_submit=True):
    # Get the YouTube URL from the user
    youtube_url = st.text_input("Enter the YouTube URL:", key="youtube_url")

    # Get the name of the playlist from the user
    playlist_name= st.text_input("Enter the name of the playlist you want to create on Spotify:", key="playlist_name")

    st.form_submit_button('Create my playlist!')

playlist= PlaylistMaker(st.session_state.playlist_name)

if 'sp' not in st.session_state:
    st.session_state.auth_url = playlist.authenticate()
    webbrowser.open(url=st.session_state.url)

else: 
    sp= st.session_state.sp
    user_info = sp.me()
    st.write(f"Hello {user_info['display_name']}!")

if 'code' in st.experimental_get_query_params():
    code = st.experimental_get_query_params()['code'][0]
    playlist.create_playlist(code)

else: 
    st.write('Something went wrong.')
    raise SystemExit



