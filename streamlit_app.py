import streamlit as st
from helpers import Processor, PlaylistMaker
import webbrowser

<<<<<<< HEAD
def main():
    st.title("Youtify 🎵")
    st.write(
        "Convert your favorite YouTube music videos to Spotify playlists!"
    )
    
    input_form= st.form(key='form', clear_on_submit=True)
    # Get the YouTube URL from the user
    youtube_url = input_form.text_input("Enter the YouTube URL:", key="youtube_url", str="https://www.youtube.com/watch?v=bmuvondrzFA")
=======
st.title("Youtify 🎵")
st.write(
    "Convert your favorite YouTube music videos to Spotify playlists!"
)
>>>>>>> 90ae1dedccf4019a9a5f7d430875d28b25a75788

input_form= st.form(key='form', clear_on_submit=True)
# Get the YouTube URL from the user
youtube_url = input_form.text_input("Enter the YouTube URL:", key="youtube_url")

# Get the name of the playlist from the user
playlist_name= input_form.text_input("Enter the name of the playlist you want to create on Spotify:", key="playlist_name")

button = input_form.form_submit_button('Create my playlist!')

if button:
    playlist= PlaylistMaker(st.session_state.playlist_name)

    if 'sp' not in st.session_state:
        auth_url = playlist.authenticate()
        # webbrowser.open(url=st.session_state.auth_url)
        st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
        print('User has been successfully authenticated')
        print(st.query_params)

    else: 
        sp= st.session_state.sp
        user_info = sp.me()
        st.write(f"Hello {user_info['display_name']}!")

    if 'code' in st.query_params:
        code = st.query_params['code'][0]
        playlist.create_playlist(code)
        st.write('Successfully created playlist')

    else: 
        st.write('Something went wrong.')
        raise SystemExit



