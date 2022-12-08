# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================== IMPORTS =====================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

import jukebox_backend as jb
import spotify_interface as sp

from datetime import datetime, timedelta
from flask import Flask
from flask import request as req
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

api = Flask(__name__)


# #==================================================================================================================# #
# #==================================================================================================================# #
# #=============================================== JUKEBOX FUNCTIONS ================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #


# sp.playback_set_volume(0)

# jukebox_skip_next()
# time.sleep(5)
# jukebox_skip_prev()

### NATURALLING ADVANCING THROUGH JUKEBOX WITH CONSTANT CHECKS FOR SCRUBBING EVERY 1 SECOND ###

# exit()



def monitor_playback():
    pass

    # pb = playback_get_state()
    # time_remaining_ms = pb["track"].duration_ms - pb["progress_ms"] 
    # print(time_remaining_ms)
    # scheduled_time = datetime.utcnow() + timedelta(milliseconds=time_remaining_ms - 2000)
    # print(scheduled_time.strftime("%H:%M:%S"))

    # def schedule_jukebox():
    #     global pb, time_remaining_ms, scheduled_time
    #     if pb["track"]:
    #         while True:
    #             pb = playback_get_state()
    #             time_remaining_ms = pb["track"].duration_ms - pb["progress_ms"] 
    #             print(time_remaining_ms)
    #             new_scheduled_time = datetime.utcnow() + timedelta(seconds=time_remaining_ms/1000 - 3)
    #             if (new_scheduled_time < scheduled_time - timedelta(seconds=1) 
    #             or new_scheduled_time > scheduled_time + timedelta(seconds=1)):
    #                 print("new scheduled time:",new_scheduled_time)
    #                 scheduled_time = new_scheduled_time
    #             if datetime.utcnow() > scheduled_time and not JUKEBOX_QUEUED:
    #                 jukebox_queue_next()
    #                 pb = playback_get_state()
    #                 time_remaining_ms = pb["track"].duration_ms - pb["progress_ms"]
    #                 time.sleep(time_remaining_ms*0.001 + 0.1)

    # def main_loop():
    #     while True:
    #         if cli() == False:
    #             exit()

    ### NATURALLING ADVANCING THROUGH JUKEBOX WITH CONSTANT CHECKS FOR SCRUBBING EVERY 1 SECOND ###
    # pb = playback_get_state()
    # while True:
    #     if pb["is_playing"]:
    #         time_remaining_ms = pb["track"].duration_ms - pb["progress_ms"] 
    #         print("seconds remaining:",round(time_remaining_ms*0.001,1))
    #         scheduled_time = datetime.utcnow() + timedelta(milliseconds=time_remaining_ms - 2000)
    #         print("scheduled time:",scheduled_time)
    #         # time.sleep(max(0,time_remaining_ms*0.001 - 2))

    #         if datetime.utcnow() > scheduled_time and not JUKEBOX_QUEUED:
    #             jukebox_queue_next()
    #             pb = playback_get_state()
    #             time_remaining_ms = pb["track"].duration_ms - pb["progress_ms"]
    #             time.sleep(time_remaining_ms*0.001 + 0.1)
    #     elif not pb["track"]:
    #         break



def init():
    if len(devices:=sp.playback_get_devices()) == 0:
        print("NO AVAILABLE PLAYBACK DEVICES! EXITING...")
        exit()
    print(devices)

    # add currently playing song to beginning of Juxebox
    jb.add_track(sp.playback_get_current_track())

    # s=sp.search("c418 aria math", num_each_items=1,types = ["track"])

    #     jb.add_track(s["tracks"][0])
    #     print(jb.get_next())
    #     print(jb.get_next().name)

    # main driver function
    if __name__ == '__main__':
    
        # run() method of Flask class runs the application
        # on the local development server.
        api.run(port=5690)
    



# @api.route("/jukebox/add", methods=["POST"])


@api.route("/jukebox/next", methods=["GET", "POST"])
def jukebox_next():
    if req.method == "POST":
        return "Skipped to next song! Now playing " + jb.skip_next().name
    else:
        return jb.get_next().__dict__

@api.route("/jukebox/previous", methods=["GET", "POST"])
def jukebox_previous():
    if req.method == "POST":
        return "Skipped to previous song! Now playing " + jb.skip_prev().name
    else:
        return jb.get_prev().__dict__

@api.route("/jukebox/current", methods=["GET"])
def jukebox_current():
    return jb.get_current().__dict__

@api.route("/jukebox/query-and-add-track")
def jukebox_query_and_add_track():
    return jb.query_and_add_track(q:=req.args.get("query"))

@api.route("/spotify/query/tracks")
def jukebox_query_tracks():
    # num_results = req.args.get("num_items")
    return sp.search(query=(q:=req.args.get("query")), types=["track"])["tracks"]



@api.route('/jukebox/auth')
def jukebox_auth_endpoint():
    code = req.args.get("code")
    user_id = req.args.get("user_id")
    print(f"{user_id} : {code}")
    return "CODE SUCCESFULLY RETRIEVED!" if code else "CODE FAILED TO BE RETRIEVED :("


# @api.route('/')
# def empty_endpoint():
#     return 'empty endpoint', 204

@api.route('/jukebox')
def jukebox_base_endpoint():
    return 'SPOTIFY JUKEBOX API ENDPOINT'




init()

# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================= Code Written by a-dubs =============================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
