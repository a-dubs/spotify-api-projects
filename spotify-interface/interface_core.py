# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================== IMPORTS =====================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
from ast import Str
from xmlrpc.client import DateTime
from database import sp_dt_to_py_dt
import spotify_web_api_handler as sp_api    
import urllib.request
import webbrowser as web
import datetime
from datetime import datetime
from datetime import timedelta
import time
from pprint import pprint
from tqdm import tqdm
import os
import json
import os.path
from os import path
from copy import copy
# #==================================================================================================================# #
# #==================================================================================================================# #
# #=================================================== CONSTANTS ====================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

ART_LOCATION = "resources/art/"
CACHE_LOCATION = "resources/cache/data/"

# #==================================================================================================================# #
# #==================================================================================================================# #
# #================================================ GLOBAL VARIABLES ================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

PLAYLISTS = {}
ALBUMS = {}
SAVED_SONGS = {}


# #==================================================================================================================# #
# #==================================================================================================================# #
#== #================================================== CLASSES =====================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

# class SpotifyArt():
#     def __init__(self, ) -> None:
#         self.sm_url
#         self.md_url 
#         self.lg_url
#         pass

sp_users_cache = {
    # id : SpotfiyUser
}
class SpotifyObject():
    def __init__(self, id : str = None, name : str = None, images : list[dict] = None) -> None:
        self.id : str = id
        self.name : str = name
        self.images : list[dict] = images

    def parse(self, info : dict):
        self.id = info["id"]
        self.name = info["name"]
        return self

class Artist(SpotifyObject):
    def __init__(self, id : str = None, name : str = None, images : list[dict] = None, popularity : int = None, genres : list[str] = None, num_followers : int = None) -> None:
        SpotifyObject.__init__(self,id, name, images)
        self.popularity : int = popularity
        self.genres : list[str] = genres
        self.num_followers : int = num_followers
    
    def parse(self, info : dict):
        super().parse(info)
        self.images = info.get("images")
        self.popularity = info.get("popularity")
        self.genres = info.get("genres")
        self.num_followers = info["followers"].get("total") if info.get("followers") else None
        return self


class Track(SpotifyObject):
    def __init__(self, id : str = None, name : str = None, images : list[dict] = None, duration_ms : int = None, popularity : int = None, track_no : int = None, explicit : bool = None, album_id : str = None, artists : list[Artist] = None) -> None:
        SpotifyObject.__init__(self,id, name, images)
        self.duration_ms : int = duration_ms
        self.popularity : int = popularity
        self.track_no : int = track_no
        self.explicit : bool = explicit
        self.album_id : str = album_id
        self.artists : list[Artist] = artists

    def parse(self, info : dict):
        # print(info)
        super().parse(info)
        self.images = info["album"].get("images") if info.get("album") else None
        self.duration_ms = info.get("duration_ms")
        self.popularity = info.get("popularity")
        self.track_no = info.get("track_number")
        self.explicit = info.get("explicit")
        self.album_id = info["album"].get("id") if info.get("album") else None
        self.artists = [Artist().parse(artist_info) for artist_info in info.get("artists")]
        self.artists_str = ", ".join([a.name for a in self.artists])
        return self

    
    def __str__(self) -> str:
        return f"< Track | {self.name} >"

class Album(SpotifyObject):
    def __init__(self, id : str = None, name : str = None, images : list[dict] = None, 
    num_tracks : int = None, album_type : str = None, release_date : str = None,
    artists : list[Artist] = None, tracks : list[Track] = None) -> None:
        SpotifyObject.__init__(self,id, name, images)
        self.num_tracks : int = num_tracks
        self.album_type : str = album_type
        self.release_date : str = release_date
        self.artists : list[Artist] = artists
        self.tracks = tracks
    
    def get_tracks(self) -> list[Track]:
        tracks = []
        while True:
            # https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-albums-tracks
            r = sp_api.get(f"https://api.spotify.com/v1/albums/{self.id}/tracks?limit=50?market=US?offset={len(tracks)}").json()
            for t in r["items"]:
                tracks.append(Track().parse(t))
            print("offset vs total:", len(tracks), r["total"])
            if r["total"] >= len(tracks):
                break
        self.tracks = tracks
        return self.tracks
        
    def parse(self, info : dict):
        super().parse(info)
        self.images = info.get("images")
        self.num_tracks = info.get("total_tracks")
        self.release_date = info.get("release_date")
        self.album_type = info.get("album_type")
        # note that self.tracks was not filled in. this only occurs when Album.get_tracks() is called
        self.artists = [Artist().parse(artist_info) for artist_info in info.get("artists")]
        return self

class Playlist(SpotifyObject):
    def __init__(self, id : str = None, name : str = None, images : list[dict] = None, 
    num_tracks : int = None, num_followers : int = None, description : str = None,
    is_public : bool = None, is_collaborative : bool = None, owner_id : str = None, owner_name : str = None, snapshot_id : str = None) -> None:
        SpotifyObject.__init__(self, id, name, images)
        self.num_tracks = num_tracks
        self.num_followers = num_followers
        self.description = description
        self.is_public = is_public
        self.is_collaborative = is_collaborative 
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.snapshot_id = snapshot_id
        self.tracks : list[PlaylistTrack] = []

    def parse(self, info: dict):
        super().parse(info)
        # print(info)
        self.images = info["images"]
        self.num_tracks = info["tracks"]["total"]
        self.num_followers = info["followers"]["total"] if "followers" in info else None
        self.is_public = info["public"]
        self.is_collaborative = info["collaborative"]
        self.description = info["description"]
        self.owner_id = info["owner"]["id"]
        self.owner_name = info["owner"]["name" if "name" in info["owner"] else "display_name"]
        self.snapshot_id = info["snapshot_id"] 
        self.tracks = []
        return self       

    # actually loads the self.tracks list with Track objects using all tracks found in this playlist
    def get_tracks(self):
        self.tracks = []
        href = f"https://api.spotify.com/v1/playlists/{self.id}/tracks"
        # initialize progress bar and request first batch of requests
        print("Getting Playlist's Tracks:")
        pb = tqdm(total = (r:=sp_api.get(href,sp_user_id="0")).json()["total"], unit = " songs")
        pb.clear()
        
        while href != None:
            r = sp_api.get(href,sp_user_id="0")
            tracks_info = r.json()
            href = tracks_info["next"]
            for track_info in tracks_info["items"]:
                if track_info["track"]:
                    self.tracks.append(PlaylistTrack().parse(track_info))
                    pb.update(1)
                else:
                    print("ERROR - empty track?")
                    print(track_info)
        return self.tracks    

    def add_tracks(self, tracks : list[Track], skip_duplicates : bool = True):
        href = f"https://api.spotify.com/v1/playlists/{self.id}/tracks"
        num_tracks_before = len(self.get_tracks())
        if skip_duplicates:
            # track_name_artists_tuples = [(track.name,track.artist) for track in tracks] 
            existing_track_ids = [track.id for track in self.tracks]
            # print(existing_track_ids)
            tracks = [track for track in tracks if not track.id in existing_track_ids]
            # print([track.id for track in tracks])
        uris = [f"spotify:track:{track.id}" for track in tracks]
        print(uris)
        for i in range(0,len(uris), 100):
            r = sp_api.post(href,sp_user_id="0",data={"uris":uris[i:min(i+100,len(uris))]})
        num_tracks_after = len(self.get_tracks())
        print(f"{(n:=num_tracks_after - num_tracks_before)} new tracks added to playlist \"{self.name}\"")
        return n

class PlaylistTrack(Track):
    def __init__(self, id: str = None, name: str = None, images: list[dict] = None, duration_ms: int = None, popularity: int = None, track_no: int = None, explicit: bool = None, album_id: str = None, artists: list[Artist] = None) -> None:
        super().__init__(id, name, images, duration_ms, popularity, track_no, explicit, album_id, artists)
        self.added_at : datetime = None
        self.added_by : SpotifyUser = None

    def parse(self, info: dict):
        track_info = info["track"]
        super().parse(track_info)
        self.added_by = SpotifyUser().parse_from_id(info["added_by"]["id"])
        self.added_at = sp_dt_to_py_dt(info["added_at"])
        return self

    def __str__(self) -> str:
        return super().__str__()    
    
    def __repr__(self) -> str:
        return super().__str__()

class SpotifyUser(SpotifyObject):
    def __init__(self, id: str = None, name: str = None, images: list[dict] = None) -> None:
        super().__init__(id, name, images)

    def parse(self, info: dict):
        return super().parse(info)
    
    def parse_from_id(self, id : str):
        if id in sp_users_cache:
            return copy(sp_users_cache[id])
        else:
            r = sp_api.get(f"/users/{id}", sp_user_id="0")
            info=r.json()
            self.id = id
            self.name = info.get("display_name")
            self.num_followers = info["followers"]["total"] if info.get("followers") else None
            self.images = info.get("images")
            sp_users_cache[id] = self
            return self



# #==================================================================================================================# #
# #==================================================================================================================# #
# #================================================ HELPER FUNCTIONS ================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

##
# Returns string representing the given datetime object or datetime.utcnow() if none provide #
def get_datetime_timestamp(dt = None):
    if not dt:
        dt = datetime.utcnow()     
    return dt.strftime("%Y-%m-%d %H:%M:%S")

##
# Fetch image from given url and stores it at given local filepath and extension # 
# Returns True if download succeeds #
# TODO : Rework this function
# str, str, [str] -> str
def download_image(url, dir_name, filename, ext = ".jpg"):
    if not path.exists(ART_LOCATION + dir_name):
        os.mkdir(ART_LOCATION + dir_name)
    if not path.exists(fp:= ART_LOCATION + dir_name + "/" + filename + ext):
        urllib.request.urlretrieve(url, fp)
    return True


##
# Download and store album art locally for use later #
def download_spotify_art(images_info, id, largest_only = False):
    sizes = []
    if largest_only:
        success = False
        if image_info["width"] and image_info["height"]:
            success = download_image(images_info[0]["url"], str((s:=images_info[0]["width"])), id)
        else: # dimensions of image are "unknown" by spotify
            success = download_image(images_info[0]["url"], (s:="misc"), id)
            # print(images_info[0])
        if success:
            sizes.append(s)
    else:
        for image_info in images_info:
            success = False
            if image_info["width"] and image_info["height"]:
                success = download_image(image_info["url"], str((s:=image_info["width"])), id)
            else: # dimensions of image are "unknown" by spotify
                success = download_image(image_info["url"], (s:="misc"), id)
                # print(image_info)
            if success:
                sizes.append(s)
    return sizes



# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================== CUSTOM SPOTIFY API INTEGRATION FUNCTIONS ====================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

##
# Save a songs to users' library given its id #

##
# Save / favorite all songs from a playlist #

##
# Gets all tracks from a given playlist using the tracks_href url #
def get_playlist_tracks(href):
    tracks = []
    
    # initialize progress bar and request first batch of requests
    pb = tqdm(total = (r:=sp_api.get(href)).json()["total"], unit = " songs")
    pb.clear()
    
    while href != None:
        r = sp_api.get(href)
        tracks_info = r.json()
        href = tracks_info["next"]
        for track_info in tracks_info["items"]:
            if track_info["track"]:
                tracks.append(simplify_playlist_track_info(track_info))
                pb.update(1)
            else:
                print("ERROR - empty track?")
                print(track_info)
    return tracks    

##
# Get user playlists #
def get_playlists(sp_user_id: str) -> list[Playlist]:
    global PLAYLISTS
    playlists = []
    next_request = "https://api.spotify.com/v1/me/playlists?offset=0&limit=50"
    
    # initialize progress bar and request first batch of requests
    print("Getting Playlists:")
    pb = tqdm(total = sp_api.get(next_request, sp_user_id=sp_user_id).json()["total"], unit = " playlists")
    pb.clear()
    
    # keep requesting while there are items left 
    while next_request != None:
        r=sp_api.get(next_request, sp_user_id=sp_user_id)
        # print(r.status_code)
        # try:
        playlists_info = r.json()
        next_request = playlists_info["next"]
        # add this batch of playlists to the master playlists list 
        for i in range(len(playlists_info["items"])):
            playlists.append(Playlist().parse(playlists_info["items"][i]))
            pb.update(1)
    
    # PLAYLISTS = {playlist["id"]: {"playlist":playlist, "last_updated": get_datetime_timestamp(datetime.utcnow())} for playlist in playlists}
    return playlists   

##
# Update a given playlist by id #
def get_playlist(id : str = "1AkipNhnPGGj71eHF7veej"):
    before = datetime.utcnow()
    PLAYLISTS[id] = simplify_playlist_info(sp_api.get("https://api.spotify.com/v1/playlists/" + id).json())
    after  = datetime.utcnow()
    print("online retrieval of playlist " + id + " took: " + str(after - before))
    return PLAYLISTS[id]


##
# Perform a search!
def search(query : str, sp_user_id : str, types : list[str] = ["track","artist","album","playlist"], 
track_query : str = "", artist_query : str = "", album_query : str = "", 
num_each_items : int = 10, offset : int = 0):
    # https://developer.spotify.com/documentation/web-api/reference/#/operations/search
    request_params = f"?q={query}"
    request_params += f"%20track:{track_query}" if track_query else ""
    request_params += f"%20artist:{artist_query}" if artist_query else ""
    request_params += f"%20album:{album_query}" if album_query else ""
    request_params += "&type=" + ",".join(types)
    request_params += f"&limit={num_each_items}"
    request_params += f"&offset={offset}"
    results = sp_api.get("https://api.spotify.com/v1/search" + request_params, sp_user_id=sp_user_id).json()
    parsed_results = {}
    # if results["tracks"]["total"] > 0:
    #     parsed_results["tracks"] = [simplify_track_info(track) for track in results["tracks"]["items"]]
    # if results["artists"]["total"] > 0:
    #     parsed_results["artists"] = [simplify_artist_info(artist) for artist in results["artists"]["items"]]
    # if results["albums"]["total"] > 0:
    #     parsed_results["albums"] = [simplify_album_info(album) for album in results["albums"]["items"]]
    # if results["playlists"]["total"] > 0:
    #     parsed_results["playlists"] = [simplify_playlist_info(playlist) for playlist in results["playlists"]["items"]]
    if "tracks" in results and results["tracks"]["total"] > 0:
        parsed_results["tracks"] = [Track().parse(track) for track in results["tracks"]["items"]]
    if "artists" in results and results["artists"]["total"] > 0:
        parsed_results["artists"] = [Artist().parse(artist) for artist in results["artists"]["items"]]
    if "albums" in results and results["albums"]["total"] > 0:
        parsed_results["albums"] = [Album().parse(album) for album in results["albums"]["items"]]
    if "playlists" in results and results["playlists"]["total"] > 0:
        parsed_results["playlists"] = [Playlist().parse(playlist) for playlist in results["playlists"]["items"]]
    return parsed_results

##
#
def get_track(track_id):
    # https://developer.spotify.com/documentation/web-api/reference/#/operations/get-track
    r = sp_api.get(f"https://api.spotify.com/v1/tracks/{track_id}")
    return Track().parse(r.json())

##
## ALL PLAYBACK/PLAYER RELATED FUNCTIONS ##
##

##
# Set playback volume of currently active device (player)
# TODO: pretty sure this does not function... get this working
def playback_set_volume(volume : int):
    # https://developer.spotify.com/documentation/web-api/reference/#/operations/set-volume-for-users-playback
    r = sp_api.put(f"https://api.spotify.com/v1/me/player/volume?volume_percent={volume}")
    print(r)
    print(r.text)

##
# Get all available playback devices for the user
def playback_get_devices():
    # https://developer.spotify.com/documentation/web-api/reference/#/operations/get-a-users-available-devices
    r = sp_api.get("https://api.spotify.com/v1/me/player/devices")
    print(r)
    return r.json().get("devices")

##
# Pause playback
def playback_pause() -> tuple[str, int]:
    # https://developer.spotify.com/documentation/web-api/reference/#/operations/pause-a-users-playback
    r = sp_api.put("https://api.spotify.com/v1/me/player/pause")
    print(r)
    if r.status_code < 300:
        msg = "Successfully paused playpack!"
    else:
        msg = "Failed to pause playback."
    return msg, r

##
# Start / Resume playback
def playback_resume() -> tuple[str, int]:
    # https://developer.spotify.com/documentation/web-api/reference/#/operations/start-a-users-playback
    r = sp_api.put("https://api.spotify.com/v1/me/player/play")
    print(r.text)
    if r.status_code < 300:
        msg = "Successfully resumed playpack!"
    else:
        msg = "Failed to resume playback."
    return msg, r
    
##
# Skip playback to next song
def playback_skip_next() -> tuple[str, int]:
    # https://developer.spotify.com/documentation/web-api/reference/#/operations/skip-users-playback-to-next-track
    r = sp_api.post("https://api.spotify.com/v1/me/player/next")
    print(r)
    if r.status_code < 300:
        msg = "Successfully skipped playback to next song!"
    else:
        msg = "Failed to skip playback to next song."
    return msg, r

##
# Skip playback to previous song (*Note: does NOT "rewind" back to beggining of current song)
def playback_skip_prev() -> tuple[str, int]:
    # https://developer.spotify.com/documentation/web-api/reference/#/operations/skip-users-playback-to-previous-track
    r = sp_api.post("https://api.spotify.com/v1/me/player/previous")
    print(r)
    if r.status_code < 300:
        msg = "Successfully skipped playback to previous song!"
    else:
        msg = "Failed to skip playback to previous song."
    return msg, r

##
# Add track to playback queue
def playback_add_to_queue(track : Track) -> tuple[str, int]:
    # https://developer.spotify.com/documentation/web-api/reference/#/operations/add-to-queue
    r = sp_api.post(f"https://api.spotify.com/v1/me/player/queue?uri=spotify:track:{track.id}")
    print(r)
    if r.status_code < 300:
        msg = f"Successfully added track '{track.name}' to queue!"
    else:
        msg = f"Failed to add track '{track.name}' playback."
    return msg, r

##
# Get currently playing track
def playback_get_current_track() -> Track:
    # https://developer.spotify.com/documentation/web-api/reference/#/operations/get-the-users-currently-playing-track
    r = sp_api.get("https://api.spotify.com/v1/me/player/currently-playing")
    return Track().parse(r.json()["item"])

##
# get all the information about the player
def playback_get_state():
    # https://developer.spotify.com/documentation/web-api/reference/#/operations/get-information-about-the-users-current-playback
    time_before = time.time_ns()
    r = sp_api.get("https://api.spotify.com/v1/me/player/currently-playing").json()
    time_after = time.time_ns() 
    skew_ms = ((time_after -  time_before)/ 1000000) / 2
    playback_info= {
        "track" : Track().parse((r["item"])),
        "device": r.get("device"),
        "is_playing": r.get("is_playing"),
        "repeat_mode" : r.get("repeat_state"),
        "shuffle_mode" : r.get("shuffle_state"),
        "progress_ms" : r["progress_ms"] + skew_ms,
        # "timestamp_fetched_ms" : r["timestamp"], # this is useful for helping knowing how many ms have passed since "progress_ms" was fetched so that this value an be offset
        "unavailable_actions" : [action for action in r["actions"].get("disallows") if r["actions"]["disallows"][action] ]
    }
    # print("time skew in ms:", skew_ms)
    return playback_info

## 
# Scrub to given position in milliseconds of current track on the currently active device/player
# TODO: idk if this works - needs tested
def playback_seek(position_ms : int):
    r=sp_api.put(f"https://api.spotify.com/v1/me/player/seek?position_ms={position_ms}")
    if r.status_code < 300:
        msg = f"Successfully seeked playback!"
    else:
        msg = f"Failed to seek playback."
    return msg, r

##
# Save a history of all the songs the user has recently listened to (a reverse (anti) queue) #

## 
# get recently played songs
def get_recent_tracks():
    print(r:=sp_api.get(endpoint="https://api.spotify.com/v1/me/player/currently-playing"))
    print(simplify_track_info(r.json()["item"]))

# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================ AUTO EXECUTE CODE BELOW =============================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #



# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================= Code Written by a-dubs =============================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
