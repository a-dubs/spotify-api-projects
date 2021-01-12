# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================== IMPORTS =====================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
import spotify_api as sp_api
import urllib.request
import requests
import base64
import webbrowser as web
import datetime
from datetime import datetime
from datetime import timedelta
import time
from tqdm import tqdm, trange
from spotify_api import WD
import os
import json
import os.path
from os import path
# #==================================================================================================================# #
# #==================================================================================================================# #
# #=================================================== CONSTANTS ====================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

ART_LOCATION = WD + "resources/art/"
CACHE_LOCATION = WD + "resources/cache/data/"

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
# #================================================ HELPER FUNCTIONS ================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

##
# Returns string representing the given datetime object or datetime.now() if none provide #
def get_datetime_timestamp(dt = None):
    if not dt:
        dt = datetime.now()     
    return dt.strftime("%Y-%m-%d %H:%M:%S")

##
# Fetch image from given url and stores it at given local filepath and extension # 
# Returns True if download succeeds #
# str, str, [str] -> str
def download_image(url, dir_name, filename, ext = ".jpg"):
    # try:
        # if not path.exists(ART_LOCATION + dir_name):
            # os.mkdir(ART_LOCATION + dir_name)
        # if not path.exists(fp:= ART_LOCATION + dir_name + "/" + filename + ext):
            # urllib.request.urlretrieve(url, fp)
        # return True
    # except:
        # print(" Downloading image failed")
        # return False
    if not path.exists(ART_LOCATION + dir_name):
        os.mkdir(ART_LOCATION + dir_name)
    if not path.exists(fp:= ART_LOCATION + dir_name + "/" + filename + ext):
        urllib.request.urlretrieve(url, fp)
    return True

##
# Fetch image from given url and stores it at given local file address and name # 
def get_image(filename, size = 640):
    pass


##
# caches all data locally to speed up retrieval #
def write_cached_data():
    if not path.exists(CACHE_LOCATION):
        os.mkdir(CACHE_LOCATION)
    # try:
    with open(CACHE_LOCATION+"playlists.json", 'w', encoding='utf-8') as playlists_file:
        json.dump(PLAYLISTS, playlists_file, ensure_ascii=False, indent=4)
        # return True
    # except:
        # return False
##
# caches all data locally to speed up retrieval #
def load_cached_data():
    global PLAYLISTS
    if not path.exists(CACHE_LOCATION+"playlists.json"):
        print("FUCK")
        return False
    # try:
    with open(CACHE_LOCATION+"playlists.json", 'r', encoding='utf-8') as playlists_file:
        PLAYLISTS = json.load(playlists_file)
        # return True
    # except:
        # print("ERROR - loading playlist cache failed")
        # return False
        
# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================== CUSTOM SPOTIFY API INTEGRATION FUNCTIONS ====================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

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


##
# Merge playlists #


##
# Auto Sync Playlists #


##
# Auto save / favorite all songs from a playlist given its id#


##
# Save a songs to users' library given its id #



##
# Save currently playing track to users' library #



##
# Save / favorite all songs from a playlist #


##
# Simplify info of a track #
def simplify_track_info(track):
    t = {}
    try: 
        t = {
            "name": track["name"],
            "id": track["id"],
            "type": track["type"],
            "track_lenth": track["duration_ms"],
            "track_number": track["track_number"],
            "explicit": track["explicit"],
            "artists": [{"name":artist["name"], "id": artist["id"]} for artist in track["artists"]],
            "album": simplify_album_info(track["album"], get_tracks = False) # don't get tracks to prevent infinite recursion 
        }            
    except:
        return t
        # print("ERROR - failed to simplify track:")
        # print(track)
    return t

##
# Simplify info of track contained in a playlist #
def simplify_playlist_track_info(track_info):
    t = simplify_track_info(track_info["track"])
    if t:
        try:
            t["date_added"] = get_datetime_timestamp(datetime.fromisoformat(track_info["added_at"]))
            t["added_by"] = track_info["added_by"]["id"]
        except:
            return t
            # print("ERROR - failed to add playlist info to track:")
            # print(track_info)
    return t
    

##
# Simplify album info from given spotify Album object #
def simplify_album_info(album, get_tracks = True):
    album_info =  {
        "name": album["name"], 
        "id": album["id"],
        "art_sizes": download_spotify_art(album["images"], album["id"]),
        "artists": [{"name":artist["name"], "id": artist["id"]} for artist in album["artists"]]
    }
    if get_tracks:
        album_info["tracks"] = [simplify_track_info(track) for track in album["tracks"]["items"]], 
    return album_info


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
# Simplify playlist info #
def simplify_playlist_info(playlist):
    # print(playlist["images"])
    return {
        "name": playlist["name"],
        "id": playlist["id"],
        "art_sizes": download_spotify_art(playlist["images"], playlist["id"]),
        "public":playlist["public"],
        "owner": playlist["owner"], # TODO: add simplify() function for users and call it here
        "editable": playlist["owner"]["id"] == sp_api.get_current_user()["id"], # maybe use bool colaborative to see if they can edit somene else's?
        "tracks": get_playlist_tracks(playlist["tracks"]["href"]),
        "track_count": playlist["tracks"]["total"]
    }

##
# Get user playlists #
def get_playlists():
    global PLAYLISTS
    playlists = []
    next_request = "https://api.spotify.com/v1/me/playlists?offset=0&limit=50"
    
    # initialize progress bar and request first batch of requests
    pb = tqdm(total = sp_api.get(next_request).json()["total"], unit = " playlists")
    pb.clear()
    
    # keep requesting while there are items left 
    while next_request != None:
        r=sp_api.get(next_request)
        # print(r.status_code)
        # try:
        playlists_info = r.json()
        next_request = playlists_info["next"]
        # add this batch of playlists to the master playlists list 
        for i in range(len(playlists_info["items"])):
            playlists.append(simplify_playlist_info(playlists_info["items"][i]))
            pb.update(1)
    
    PLAYLISTS = {playlist["id"]: {"playlist":playlist, "last_updated": get_datetime_timestamp(datetime.now())} for playlist in playlists}
    return playlists   


##
# Save a history of all the songs the user has recently listened to (a reverse (anti) queue) #


##
# Update a given playlist by id #
def get_playlist(id="1AkipNhnPGGj71eHF7veej"):
    before = datetime.now()
    PLAYLISTS[id] = simplify_playlist_info(sp_api.get("https://api.spotify.com/v1/playlists/" + id).json())
    after  = datetime.now()
    print("online retrieval of playlist " + id + " took: " + str(after - before))


# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================ AUTO EXECUTE CODE BELOW =============================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #


# print(before:=datetime.now())
# get_playlists()
# print(PLAYLISTS)
# print(after:=datetime.now())
# print("online retrieval took: " + str(after - before))
# write_cached_data()
# print(afterafter:=datetime.now())
# print("cahing data took: " + str(afterafter - after))
# PLAYLISTS = {}
# load_cached_data()
# print(len(PLAYLISTS.keys()))
# print(afterafterafter:=datetime.now())
# print("loading cached data took: " + str(afterafterafter - afterafter))

get_playlist()




# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================= Code Written by A-Dubs =============================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
