import os
import sys
import json
import webbrowser
import pandas as pd
import seaborn as sb
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from flask import Flask, render_template, url_for, request, redirect, session
import time

app = Flask(__name__)

app.secret_key = 'key'

API_BASE = 'https://accounts.spotify.com'

clientID ="4b3a1682d17c4711b3943fdc7eec3cde" 
secretID = "7f3bcf6e081846b88b6dcf3a658203a5"

# Make sure you add this to Redirect URIs in the setting of the application dashboard
#REDIRECT_URI = "http://127.0.0.1:5000/api_callback"
REDIRECT_URI = "https://spotmytracks.herokuapp.com/api_callback"

os.environ['SPOTIPY_CLIENT_ID']= clientID
os.environ['SPOTIPY_CLIENT_SECRET']= secretID
os.environ['SPOTIPY_REDIRECT_URI']= REDIRECT_URI

SCOPE = 'playlist-modify-private,playlist-modify-public,user-top-read'

# Set this to True for testing but you probaly want it set to False in production.
SHOW_DIALOG = True

# authorization-code-flow Step 1. Have your application request authorization; 
# the user logs in and authorizes access
@app.route("/")
def verify():
    print("verify()")
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = clientID, client_secret = secretID, redirect_uri = REDIRECT_URI, scope = SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)

# authorization-code-flow Step 2.
# Have your application request refresh and access tokens;
# Spotify returns access and refresh tokens
@app.route("/api_callback")
def api_callback():
    print("/api_callback")
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = clientID, client_secret = secretID, redirect_uri = REDIRECT_URI, scope = SCOPE)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    # Saving the access token along with all other token related info
    session["token_info"] = token_info
    return redirect("index")

@app.route("/index")
def index():
    print("/index")

    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')
    data = request.form
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    user = sp.current_user()
    userList = []
    userList.append(user)
    with open('user_data.json', 'w', encoding='utf-8') as f:
        json.dump(userList, f, ensure_ascii=False, indent=4)

    with open('user_data.json') as l:
        userData = json.load(l)

    user_display_name = userData[0]["display_name"]
    print(user_display_name+ "'s Top Songs!" )

    #clean up or else stays stuck on a user
    os.remove("user_data.json")
    os.system("rm -rf .cache")

    return render_template("index.html", user=user_display_name)

# authorization-code-flow Step 3.
# Use the access token to access the Spotify Web API;
# Spotify returns requested data
@app.route("/go", methods=['POST'])
def go():

    username = ""
    list_of_results = []
    list_of_artist_names = []
    list_of_artist_uri = []
    list_of_song_names = []
    list_of_song_uri = []
    list_of_durations_ms = []
    list_of_explicit = []
    list_of_albums = []
    list_of_popularity = []
    list_of_artwork = []
    list_of_release_dates = []

    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')
    data = request.form
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = sp.current_user_top_tracks(limit=10,offset=0,time_range=data['time_range'])
    time_name = str(data['time_range'])
    user = sp.current_user()
    userList = []
    userList.append(user)

    with open('user_data.json', 'w', encoding='utf-8') as f:
        json.dump(userList, f, ensure_ascii=False, indent=4)

    for song in range(10):
        list = []
        list.append(results)
        with open('top10_data.json', 'w', encoding='utf-8') as f:
            json.dump(list, f, ensure_ascii=False, indent=4)
    
    with open('top10_data.json') as f:
        data = json.load(f)

    with open('user_data.json') as l:
        userData = json.load(l)

    list_of_results = data[0]["items"]
    user_display_name = userData[0]["display_name"]
    print(user_display_name+ "'s Top Songs!" )

    for result in list_of_results:

        this_artists_name = result["artists"][0]["name"]
        list_of_artist_names.append(this_artists_name)

        this_artists_uri = result["artists"][0]["uri"]
        list_of_artist_uri.append(this_artists_uri)

        list_of_songs = result["name"]
        list_of_song_names.append(list_of_songs)

        song_uri = result["uri"]
        list_of_song_uri.append(song_uri)

        list_of_duration = result["duration_ms"]
        list_of_durations_ms.append(list_of_duration)

        this_album = result["album"]["name"]
        list_of_albums.append(this_album)

        this_release_date = result["album"]["release_date"]
        list_of_release_dates.append(this_release_date)

        this_album_artwork = result["album"]["images"][0]["url"]
        list_of_artwork.append(this_album_artwork)
        #webbrowser.open(this_album_artwork)

        song_popularity = result["popularity"]
        list_of_popularity.append(song_popularity)

        #print(this_artists_name + ': ' + list_of_songs + ", " + this_album + ", released: " + this_release_date + ", " + this_album_artwork)

    
    #only metadata i need
    top_songs_pretty = pd.DataFrame(
    {   'artist': list_of_artist_names,
        'song': list_of_song_names,
        'album': list_of_albums,
        'artwork': list_of_artwork,
    })

    #full metadata of song
    all_songs_meta = pd.DataFrame(
    {'artist': list_of_artist_names,
        'artist_uri': list_of_artist_uri,
        'song': list_of_song_names,
        'song_uri': list_of_song_uri,
        'duration_ms': list_of_durations_ms,
        'album': list_of_albums,
        'release_date': list_of_release_dates,
        'artwork': list_of_artwork,
        'popularity': list_of_popularity 
    })

    all_songs_saved = all_songs_meta.to_csv('top10_songs.csv')

    #clean up or else stays stuck on a user
    os.remove("top10_data.json")
    os.remove("top10_songs.csv")
    os.remove("user_data.json")
    os.system("rm -rf .cache")
   
    # print(json.dumps(response))
    #return render_template("results.html", data=data)
    print(time_name)
    return render_template("index.html", column_names=top_songs_pretty.columns.values, row_data=top_songs_pretty.values.tolist(),
                           link_column="", zip=zip, user=user_display_name, time_name=time_name)
   

# Checks to see if token is valid and gets a new token if not
def get_token(session):
    print('getToken()')
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = clientID, client_secret = secretID, redirect_uri = REDIRECT_URI, scope = SCOPE)
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid

#dont work
def fillData(list_of_results):
    for result in list_of_results:

        this_artists_name = result["artists"][0]["name"]
        list_of_artist_names.append(this_artists_name)

        this_artists_uri = result["artists"][0]["uri"]
        list_of_artist_uri.append(this_artists_uri)

        list_of_songs = result["name"]
        list_of_song_names.append(list_of_songs)

        song_uri = result["uri"]
        list_of_song_uri.append(song_uri)

        list_of_duration = result["duration_ms"]
        list_of_durations_ms.append(list_of_duration)

        this_album = result["album"]["name"]
        list_of_albums.append(this_album)

        this_release_date = result["album"]["release_date"]
        list_of_release_dates.append(this_release_date)

        this_album_artwork = result["album"]["images"][0]["url"]
        list_of_artwork.append(this_album_artwork)
        #webbrowser.open(this_album_artwork)

        song_popularity = result["popularity"]
        list_of_popularity.append(song_popularity)

        #print(this_artists_name + ': ' + list_of_songs + ", " + this_album + ", released: " + this_release_date + ", " + this_album_artwork)

if __name__ == "__main__":
    app.run(debug=True)
