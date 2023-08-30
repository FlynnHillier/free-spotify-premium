import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()


OAUTH = SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        open_browser=True,
        scope="playlist-modify-private,playlist-read-private,playlist-modify-public,user-library-modify,user-library-read",
        username=os.getenv("SPOTIFY_USERNAME"),
    )

default_client = spotipy.Spotify(
    client_credentials_manager=OAUTH
)

def rip_playlist(playlist_id:str,playlist_name:str | None = None,spotipy_client: spotipy.Spotify | None = None) -> bool:
    """copy a playlist from another user to your own account.

    Args:
        playlist_id (str): the id of the playlist to copy
        playlist_name (str | None, optional): A custom name for the playlist, if None will copy the existing playlist name. Defaults to None.

    Returns:
        bool: True
    """

    if spotipy_client == None:
        spotipy_client = default_client

    current_user = spotipy_client.me()

    target_playlist = spotipy_client.playlist(playlist_id=playlist_id)
    
    #pull all track ids from within target playlist
    track_uris : list[str] = []
    for item in target_playlist["tracks"]["items"]:
        track = item["track"]
        track_uris.append(track["uri"])
    

    if playlist_name == None:
        #copy playlist name
        playlist_name = target_playlist["name"]

    #create new playlist
    new_playlist = spotipy_client.user_playlist_create(current_user["id"],playlist_name,description="flynnhillier")

    if(len(track_uris) > 0):
        spotipy_client.playlist_add_items(playlist_id=new_playlist["id"],items=track_uris)

    return True



def rip_all_playlists(target_user_id:str,spotipy_client: spotipy.Spotify | None = None) -> int:
    """rip all the playlists publicly available within the target_user_id's profile.

    Args:
        target_user_id (str): the id of the user to rip playlists from

    Returns:
        bool: True
    """

    if spotipy_client == None:
        spotipy_client = default_client
    

    target_playlists = spotipy_client.user_playlists(target_user_id)

    playlist_ids : list[str] = []

    for item in target_playlists["items"]:
        playlist_ids.append(item["id"])

    for playlist_id in playlist_ids:
        rip_playlist(playlist_id,spotipy_client=spotipy_client)
    
    return len(playlist_ids)