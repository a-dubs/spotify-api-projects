import requests
import os
import base64
import webbrowser as web
import datetime
from datetime import datetime
from datetime import timedelta
import re
import time
import json

import database as db
from secrets_handler import decode_secrets, client_id, client_secret, redirect_uri
decode_secrets() 

os.chdir(os.path.dirname(os.path.realpath(__file__)))

# #==================================================================================================================# #
# #==================================================================================================================# #
# #=================================================== CONSTANTS ====================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

REFRESH_TOKEN_FILEPATH = "resources/cache/refresh_token.txt"
scope = "user-read-playback-state user-read-private user-top-read user-read-currently-playing playlist-read-private user-follow-read user-read-recently-played user-library-read app-remote-control user-modify-playback-state playlist-modify-public playlist-modify-private"

# #==================================================================================================================# #
# #================================================ GLOBAL VARIABLES ================================================# #
# #==================================================================================================================# #


# #==================================================================================================================# #
# #==================================================================================================================# #
# #================================================ HELPER FUNCTIONS ================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #


# #==================================================================================================================# #
# #============== get authorization url from spotify authorize endpoint for given scope (permissions) ===============# #
# -> String #
def get_auth_url(sp_user_id : str):
    auth = requests.get("https://accounts.spotify.com/authorize", 
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": scope,
            "show_dialog": False,
            "state" : f"{db.cache_auth_code_random_state_string(sp_user_id)}:{sp_user_id}"})

    print(auth.status_code)
    return auth.url
 
# #==================================================================================================================# #
# #=========== get authorization code from auth url redirect after permissions have been granted by user ============# #
# -> String #
def get_auth_code(sp_user_id : str):
    url = f"{get_auth_url(sp_user_id)}?sp_user_id={sp_user_id}"
    print("opening:",url)
    web.open_new(url)
    print("sent code off to auth handler api's endpoint. waiting for code to be extracted and saved to db file...")
    while True:
        if code:=db.get_sp_token_info(sp_user_id).get("code"):
            break
        time.sleep(0.1)
    print("code: " + code)
    return code
        
# #==================================================================================================================# #
# #============================ make HTTP header for Spotify API authorization requests =============================# #
# -> Dict #
def make_auth_headers():
    b64_client_creds = str(base64.b64encode((client_id+":"+client_secret).encode("ascii")), "ascii")
    headers = {
        "Authorization":"Basic " + b64_client_creds,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    return headers 

# #==================================================================================================================# #
# #========================== make HTTP header for non-authorization Spotify API requests ===========================# #
# -> Dict #
def make_api_headers(sp_user_id : str):
    if db.get_sp_token_info(sp_user_id).get("access_token"):
        return {"Accept": "application/json","Content-Type": "application/json", "Authorization": "Bearer " + get_access_token(sp_user_id)}
    else:
        print("something went wrong making header for spotify api, does the access token exist?")
        return {}

# #==================================================================================================================# #
# #================= get spotify token from API; used only once - use refresh_spotify_token() after =================# #
# -> Dict #
def request_spotify_token(sp_user_id : str):

       
    # try to get refresh token if it already exists
    if db.sp_token_exists(sp_user_id=sp_user_id) and (rt:=db.get_sp_token_info(sp_user_id).get("refresh_token")) and len(rt) > 0:
        refresh_spotify_token(sp_user_id)
    
    # no stored refresh token found
    else:
        # request new access token info from Spotify API
        b64_client_creds = str(base64.b64encode((client_id+":"+client_secret).encode("ascii")), "ascii")
        headers = {
            "Authorization":"Basic " + b64_client_creds
        }
        r = post("https://accounts.spotify.com/api/token", 
            sp_user_id=sp_user_id,
            headers = headers,
            data = {
                "grant_type": "authorization_code",
                "code": get_auth_code(sp_user_id=sp_user_id),
                "redirect_uri": redirect_uri
            })
        print("fetching spotify token: "+ str(r.status_code))
        
        try:
            t = r.json()
            # take 5 seconds off expiring time to make sure an expired token will never try to be used 
            expires_at = datetime.utcnow() + timedelta(seconds = t["expires_in"] - 5)
            #update db entry for token info
            db.update_sp_token_info(t["access_token"], t["refresh_token"], expires_at, t["scope"], sp_user_id=sp_user_id)

        except:
            print(r.text)
            print("Something went wrong when trying fetch access token!")
     
            
    return db.get_sp_token_info(sp_user_id)

# #==================================================================================================================# #
# #======================= call this function to get new access code once old one has expired =======================# #
# -> Dict #
def refresh_spotify_token(sp_user_id : str):
    r = post("https://accounts.spotify.com/api/token", 
        sp_user_id=sp_user_id,
        headers = make_auth_headers(),
        data = {
            "grant_type": "refresh_token",
            "refresh_token": (rt:=db.get_sp_token_info(sp_user_id)["refresh_token"])
    })
    print("refreshing spotify token: "+ str(r.status_code))
    if r.status_code >= 300:
        print(r.text)
    # try:
    t = r.json()
    print("token info recvd from spotify:", t)
    # take 5 seconds off expiring time to make sure an expired token will never try to be used 
    expires_at = datetime.utcnow() + timedelta(seconds = t["expires_in"] - 5)
    #update db entry for token info
    db.update_sp_token_info(t["access_token"], rt, expires_at, t["scope"], sp_user_id=sp_user_id)
    # except Exception as e:
    #     print("Something went wrong when trying refresh access token!")
    #     print(e)
    return db.get_sp_token_info(sp_user_id)

# #==================================================================================================================# #
# #=========== updates spotify_token if access token has expired; returns access token from spotify_token ===========# #
# #===== call this function to get access token. do not call request_spotify_token() or refresh_spotify_token() =====# #
# -> String #
def get_access_token(sp_user_id : str):    
    # no access token exists; go fetch one
    if False == db.sp_token_exists(sp_user_id=sp_user_id): # db.get_sp_token_info(sp_user_id).get("access_token") in (None, ""):
        print("no access token exists!")
        request_spotify_token(sp_user_id)
    
    # refresh access token
    elif datetime.utcnow() > db.get_sp_token_info(sp_user_id)["expires_at"]:
        print("spotify token expired! fetching updated one now!")
        refresh_spotify_token(sp_user_id)
    
    return db.get_sp_token_info(sp_user_id)["access_token"]


# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================= SPOTIFY API FUNCTIONS ==============================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

# call to the spotify API at the given endpoint using the given http method #
# String, Dict, Dict, String -> Http Response object #
def call_api(endpoint, sp_user_id : str, method, headers={}, data={}):
    if not "spotify" in endpoint:
        endpoint = "https://api.spotify.com/v1" + endpoint
    method=method.upper()
    if not headers:
        headers = make_api_headers(sp_user_id)
    if method=="GET":
        return requests.get(endpoint, data=data, headers = headers)
    elif method=="POST":
        return requests.post(
            url=endpoint, 
            data=json.dumps(data) if re.search(".*/playlists/.*/tracks",endpoint) else data,  # account for special case
            headers = headers
        )
    elif method=="PUT":
        return requests.put(endpoint, data=data, headers = headers)
    elif method=="DELETE" or method=="DEL":
        return requests.delete(endpoint, data=data, headers = headers)
    else:
        print("ERROR - invalid http method given.")
        

##
# calls HTTP GET request to given endpoint with given data if any #
# String, Dict, Dict -> Http Response object #
def get(endpoint, sp_user_id : str, headers = {}, data={}):
    return call_api(endpoint, sp_user_id,"GET", headers, data)
    
    
    ##
# calls HTTP POST request to given endpoint with given data if any #
# String, Dict, Dict -> Http Response object #
def post(endpoint, sp_user_id : str, headers = {}, data={}):
    return call_api(endpoint, sp_user_id, "POST", headers, data)
 
##
# calls HTTP PUT request to given endpoint with given data if any #
# String, Dict, Dict -> Http Response object #
def put(endpoint, sp_user_id : str, headers = {}, data={}):
    return call_api(endpoint, sp_user_id, "PUT", headers, data)

## 
# calls HTTP DELETE request to given endpoint with given data if any #
# String, Dict, Dict -> Http Response object #
def delete(endpoint, sp_user_id : str, headers = {}, data={}):
    return call_api(endpoint, sp_user_id, "DELETE", headers, data)

    
##
# get info about the user using the API currently #
# -> Http Response object #
def get_current_user(sp_user_id : str):
    return get("https://api.spotify.com/v1/me", sp_user_id=sp_user_id).json()



# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================ AUTO EXECUTE CODE BELOW =============================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #



# initialize token information to allow access to Spotify API
jb_test_id = "0"
get_access_token(jb_test_id)
print("Currently logged in to Spotify as " + get_current_user(jb_test_id)["display_name"])


# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================= Code Written by A-Dubs =============================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #