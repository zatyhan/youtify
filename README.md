# Youtify (WIP)

A web app to convert your favorite youtube playlist into your own spotify playlist. 

Currently still in development mode, although it is already up and running [here](https://youtify-740108645575.us-central1.run.app/). However, the dockerized app works perfectly fine on own's local machine. 

### How to run it on your own machine

1. Clone the repository

   ```
   $ git clone https://github.com/zatyhan/youtify.git
   ```

2. Create an .env file with your own [Shazam Rapid API key](https://rapidapi.com/apidojo/api/shazam) and set the Spotify app credentials as below: 

   ```
   # flask app configuration 
   PORT=yourport
   SESSION_TYPE="redis"
   SESSION_USE_SIGNER="True"
   PERMANENT_SESSION_LIFETIME="3600"
   # flask secret key for caching 
   SECRET_KEY="yourkey"
   # rapid api key
   RAPIDAPI_KEY="yourkey"
   # Spotify app credentials
   SPOTIPY_CLIENT_ID="d3eb6ef85c20439d89f4c6b100024b20"
   SPOTIPY_CLIENT_SECRET="4e00a9fa8ddf46388b293490d3cc5465"
   SPOTIPY_REDIRECT_URI="http://127.0.0.1:$(PORT)/callback"
   
   ```

3. Run the docker command to build the container and ensure you have your docker dekstop/engine running:
```
$ docker-compose up --build
```
4. Open your browser and navigate to `http://localhost:yourport/` to access the app.