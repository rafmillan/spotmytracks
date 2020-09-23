import os
import sys
import json
import webbrowser
import pandas as pd
import seaborn as sb
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

clientID ="4b3a1682d17c4711b3943fdc7eec3cde" 
secretID = "7f3bcf6e081846b88b6dcf3a658203a5"

os.environ['SPOTIPY_CLIENT_ID']= clientID
os.environ['SPOTIPY_CLIENT_SECRET']= secretID

os.environ['SPOTIPY_REDIRECT_URI']='http://localhost:8888/callback'

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

username = ""
client_credentials_manager = SpotifyClientCredentials(client_id=clientID, client_secret=secretID) 
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
scope = 'user-top-read'
# Erase .cache to prompt for user permission
try:
    token = util.prompt_for_user_token(username, scope) # add scope
except (AttributeError, JSONDecodeError):
    os.remove(".cache")
    token = util.prompt_for_user_token(username, scope) # add scope


if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_top_tracks(limit=10,offset=0,time_range='medium_term')
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

else:
    print("Can't get token for", username)

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
    webbrowser.open(this_album_artwork)

    song_popularity = result["popularity"]
    list_of_popularity.append(song_popularity)

    print(this_artists_name + ': ' + list_of_songs + ", " + this_album + ", released: " + this_release_date + ", " + this_album_artwork)

all_songs = pd.DataFrame(
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

all_songs_saved = all_songs.to_csv('top10_songs.csv')



# lz_uri = 'spotify:artist:48dgx7iGqLQ3E5KO3pzd94'

# spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
# results = spotify.artist_top_tracks(lz_uri)

# for track in results['tracks'][:10]:
#     print('track    : ' + track['name'])
#     print('audio    : ' + track['preview_url'])
#     print('cover art: ' + track['album']['images'][0]['url'])
#     print()
