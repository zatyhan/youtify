import streamlit as st
from helpers import Processor, PlaylistMaker
import asyncio

    
@st.cache_data
def get_cached_playlist():
    return None

def set_cached_playlist(playlist):
    get_cached_playlist.clear()
    get_cached_playlist._cache[0]= playlist

# @st.cache_data
# def authenticator():


def main():
    st.title("Youtify 🎵")
    st.write(
        "Convert your favorite YouTube music videos to Spotify playlists!"
    )

    if 'playlist' not in st.session_state:
        st.session_state.playlist= get_cached_playlist()

    input_form= st.form(key='form', clear_on_submit=True)
    youtube_url = input_form.text_input("Enter the YouTube URL:", key="youtube_url", value= "https://www.youtube.com/watch?v=rMZeKQYLXWc")
    playlist_name= input_form.text_input("Enter the name of the playlist you want to create on Spotify:", key="playlist_name", value= "My Playlist")
    button = input_form.form_submit_button('Create my playlist!')

    if button:
        st.session_state.playlist= PlaylistMaker(st.session_state.playlist_name)
        set_cached_playlist(st.session_state.playlist)
        print('1: ', st.session_state.playlist)
        if 'sp' not in st.session_state:
            auth_url = st.session_state.playlist.authenticate()
            print('authenticating...')
            st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">',  unsafe_allow_html=True)
            print('2:', st.session_state.playlist)
            st.stop()
    
    print('3: ', st.session_state.playlist)
    
    # after redirection
    query_params = st.query_params
    if 'code' in query_params:
        print('creating playlist....')
        st.session_state.playlist = get_cached_playlist()
        
        if st.session_state.playlist is not None:
            code = query_params['code']
            if 'sp' not in st.session_state:
                st.session_state.playlist.create_playlist(code)
                st.write('Successfully created playlist')
                st.session_state.sp = st.session_state.playlist.sp  # Store the authenticated session
            else:
                sp = st.session_state.sp
                user_info = sp.me()
                st.write(f"Hello {user_info['display_name']}!")            
    else:
        st.write('Waiting for authentication...')

if __name__==  "__main__":
    main()

