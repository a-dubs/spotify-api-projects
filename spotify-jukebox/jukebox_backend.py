# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================== IMPORTS =====================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

import jukebox_backend as jb
import spotify_interface as sp
from spotify_interface import Track, Artist, Album, Playlist

from datetime import datetime, timedelta

# #==================================================================================================================# #
# #==================================================================================================================# #
# #=================================================== CONSTANTS ====================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

# #==================================================================================================================# #
# #==================================================================================================================# #
# #================================================ GLOBAL VARIABLES ================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

JUKEBOX = [
    # {
        # played_timestamp_ms : int,  # unix timestamp in ms when song started playing
        # track : track_info obj
    # }
]
JUKEBOX_POS = 0
JUKEBOX_QUEUED = False

# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================== BACK-END FUNCTIONS =============================================== # #
# #==================================================================================================================# #
# #==================================================================================================================# #



# #==================================================================================================================# #
# #==================================================================================================================# #
# #=================================================== FUNCTIONS ====================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #


##
# Save currently playing track to users' library #
def like_current_track():
    pass


##
# Get current track in Jukebox
def get_current() -> Track:
    if sp.playback_get_current_track() != (t:=(JUKEBOX[JUKEBOX_POS] if JUKEBOX_POS < len(JUKEBOX) and JUKEBOX_POS >= 0 else None)):
        print("HUH???? is jukebox out of sync?")
    return t


##
# Get prev track in Jukebox
def get_prev() -> Track:
    return JUKEBOX[JUKEBOX_POS-1] if JUKEBOX_POS-1 >= 0 else None

##
# Get next track in Jukebox
def get_next() -> Track:
    print("jb pos",JUKEBOX_POS)
    print("len jb",len(JUKEBOX))
    return JUKEBOX[JUKEBOX_POS+1] if JUKEBOX_POS+1 < len(JUKEBOX) else None

##
# Queue up the next item in jukebox's list (in preparation for advancing/skipping to it)
def queue_next() -> Track:
    global JUKEBOX, JUKEBOX_QUEUED, JUKEBOX_POS
    print(sp.playback_add_to_queue(get_next()))
    JUKEBOX_QUEUED = True
    JUKEBOX_POS +=1

##
# Queue up the prev item in jukebox's list (in preparation for skipping to it)
def queue_prev() -> Track:
    global JUKEBOX, JUKEBOX_QUEUED, JUKEBOX_POS
    print(sp.playback_add_to_queue(get_next()))
    JUKEBOX_QUEUED = True
    JUKEBOX_POS -=1

## 
# Advance immediately to the next song in the jukebox 
def skip_next() -> Track:
    global JUKEBOX, JUKEBOX_QUEUED, JUKEBOX_POS
    if not JUKEBOX_QUEUED:
        # get next song in jukebox and add it to spotify queue
        queue_next()
    # manipulate the playback api and skip to "next song" i.e song that was just added to queue
    sp.playback_skip_next()
    JUKEBOX_QUEUED = False
    return sp.playback_get_current_track()

## 
# Advance immediately to the next song in the jukebox 
def skip_prev() -> Track:
    global JUKEBOX, JUKEBOX_QUEUED, JUKEBOX_POS
    if not JUKEBOX_QUEUED:
        # get preceding song in jukebox and add it to spotify queue
        queue_prev()
    # manipulate the playback api and skip to "next song" i.e. song that was just added to queue
    sp.playback_skip_next()
    JUKEBOX_QUEUED = False
    return sp.playback_get_current_track()

##
# Add track to end of Jukebox's list
def add_track(track = None, track_id = None) -> Track:
    global JUKEBOX, JUKEBOX_QUEUED, JUKEBOX_POS
    if track != None:
        JUKEBOX.append(track)
        return track
    elif track_id != None:
        JUKEBOX.append(t:=sp.get_track(track_id))
        return t
    else:
        print("ERROR! NO TRACK GIVEN!")
        return None

##
# Get first Track result from search queury and add it to the end of Jukebox's list
def query_and_add_track(query : str) -> Track:
    global JUKEBOX, JUKEBOX_QUEUED, JUKEBOX_POS
    result = sp.search(query=query,types=["track"])["tracks"][0]
    JUKEBOX.append(result)
    return result




# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================= Code Written by a-dubs =============================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
