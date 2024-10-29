import streamlit as st

st.title("Youtify 🎵")
st.write(
    "Convert your favorite YouTube music videos to Spotify playlists!"
)

# Get the YouTube URL from the user
youtube_url = st.text_input("Enter the YouTube URL:")
