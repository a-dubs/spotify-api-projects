import requests
import os
import base64
import webbrowser as web
import datetime
from datetime import datetime
from datetime import timedelta
import time
from tqdm import tqdm, trange

# #==================================================================================================================# #
# #==================================================================================================================# #
# #=================================================== CONSTANTS ====================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
WD = "C:/Users/alecw/Google Drive/Coding and Projects/Spotify Custom App/"
REFRESH_TOKEN_FILEPATH = WD + "/resources/cache/refresh_token.txt"
client_id = "639271c751444229bf7a79bf2d0c3f31"
client_secret = "4cf44001c67d4bb1b71dde09374840a9"
scope = "user-read-playback-state user-read-private user-top-read user-read-currently-playing playlist-read-private user-follow-read user-read-recently-played user-library-read"
redirect_uri = "https://google.com"



# #==================================================================================================================# #
# #==================================================================================================================# #
# #================================================ GLOBAL VARIABLES ================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

# spotify api auth token and related info
spotify_token = {}
app_authorized_by_user = True



# #==================================================================================================================# #
# #==================================================================================================================# #
# #================================================ HELPER FUNCTIONS ================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #




# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================= SPOTIFY API FUNCTIONS ==============================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #


# #==================================================================================================================# #
# #============== get authorization url from spotify authorize endpoint for given scope (permissions) ===============# #
# -> String #
def get_auth_url():
    auth = requests.get("https://accounts.spotify.com/authorize", 
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": "https://google.com",
            "scope": scope,
            "show_dialog": False })

    print(auth.status_code)
    return auth.url
 
# #==================================================================================================================# #
# #=========== get authorization code from auth url redirect after permissions have been granted by user ============# #
# -> String #
def get_auth_code():
    if app_authorized_by_user:
        # url = get_auth_url()
        # r = requests.post(url, data={"username":"alecwarren19@gmail", "password":"Steelix1434$$$"})
        # print(r.status_code)
        # driver = webdriver.Firefox(executable_path = r'C:\Users\alecw\Downloads\geckodriver-v0.26.0-win64\geckodriver.exe', service_args=[r"--log-path=C:\Users\alecw\Google Drive\Coding and Projects\Led Display Project & Spotfy API\geckodriver.log"])
        # driver.get(get_auth_url())
        # time.sleep(5);
        # print(redirect_url:=(driver.current_url))
        web.open_new(get_auth_url())
        print("Copy and paste url from redirected website below: ")
        redirect_url = str(input())
        code = redirect_url[redirect_url.find("=")+1:]
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
def make_api_headers():
    if spotify_token.get("access_token"):
        return {"Accept": "application/json","Content-Type": "application/json", "Authorization": "Bearer " + get_access_token()}
    else:
        print("something went wrong making header for spotify api, does the access token exist?")
        return {}

# #==================================================================================================================# #
# #================= get spotify token from API; used only once - use refresh_spotify_token() after =================# #
# -> Dict #
def request_spotify_token():
    global spotify_token
       
    # open file containing stored access token 
    try:
        refresh_token_txt = open(REFRESH_TOKEN_FILEPATH, "r")
        spotify_token["refresh_token"] = (rt:=refresh_token_txt.readline())
        # print(rt)
        refresh_token_txt.close()
        refresh_spotify_token()
     
    # no stored refresh token found
    except:
        print("Refresh token file not found... Creating new one now.")
        refresh_token_txt = open(REFRESH_TOKEN_FILEPATH, "w+")
        refresh_token_txt.close()
        # request new access token info from Spotify API
        b64_client_creds = str(base64.b64encode((client_id+":"+client_secret).encode("ascii")), "ascii")
        headers = {
            "Authorization":"Basic " + b64_client_creds
        }
        r = post("https://accounts.spotify.com/api/token", 
            headers = headers,
            data = {
                "grant_type": "authorization_code",
                "code": get_auth_code(),
                "redirect_uri": redirect_uri
            })
        print("fetching spotify token: "+ str(r.status_code))
        
        try:
            token_info = r.json()
            
            spotify_token["access_token"] = token_info["access_token"]
            spotify_token["refresh_token"] = token_info["refresh_token"]
            spotify_token["scope"] = token_info["scope"]
            # take 5 seconds off expiring time to make sure an expired token will never try to be used 
            spotify_token["expires at"] = datetime.now() + timedelta(seconds = token_info["expires_in"] - 5)
        except:
            print("Something went wrong when trying fetch access token!")
        cache_refresh_token()
            
    return spotify_token

# #==================================================================================================================# #
# #======================= call this function to get new access code once old one has expired =======================# #
# -> Dict #
def refresh_spotify_token():
    global spotify_token
    r = post("https://accounts.spotify.com/api/token", 
        headers = make_auth_headers(),
        data = {
            "grant_type": "refresh_token",
            "refresh_token": spotify_token["refresh_token"]
    })
    print("refreshing spotify token: "+ str(r.status_code))
    try:
        token_info = r.json()
        spotify_token["access_token"] = token_info["access_token"]
        spotify_token["scope"] = token_info["scope"]
        # take 5 seconds off expiring time to make sure an expired token will never occur 
        spotify_token["expires at"] = datetime.now() + timedelta(seconds = token_info["expires_in"] - 5)
        # print("new token fetched: " + spotify_token["access_token"])
    except:
        print("Something went wrong when trying refresh access token!")
    return spotify_token

# #==================================================================================================================# #
# #=========== updates spotify_token if access token has expired; returns access token from spotify_token ===========# #
# #===== call this function to get access token. do not call request_spotify_token() or refresh_spotify_token() =====# #
# -> String #
def get_access_token():    
    # no access token exists; go fetch one
    if spotify_token.get("access_token") == None:
        print("no access token exists!")
        request_spotify_token()
    
    # refresh access token
    elif datetime.now() > spotify_token["expires at"]:
        print("spotify token expired! fetching updated one now!")
        refresh_spotify_token()
    
    
    return spotify_token["access_token"]


# #==================================================================================================================# #
# #=== updates token refresh code in the local token file - this will allow for the user to remain authenticated ====# #
# #============================= between sessions by accessing the cached refresh token =============================# #
def cache_refresh_token():
    print("caching spotify refresh token: " + spotify_token["refresh_token"])
    file = open(REFRESH_TOKEN_FILEPATH, "w")
    file.write(spotify_token["refresh_token"])
    file.close()

## 
# call to the spotify API at the given endpoint using the given http method #
# String, Dict, Dict, String -> Http Response object #
def call_api(endpoint, method, headers={}, data={}):
    
    method=method.upper()
    if not headers:
        headers = make_api_headers()
    
    if method=="GET":
        return requests.get(endpoint, data=data, headers = headers)
    elif method=="POST":
        return requests.post(endpoint, data=data, headers = headers)
    elif method=="PUT":
        return requests.put(endpoint, data=data, headers = headers)
    elif method=="DELETE" or method=="DEL":
        return requests.delete(endpoint, data=data, headers = headers)
    else:
        print("ERROR - invalid http method given.")

##
# calls HTTP GET request to given endpoint with given data if any #
# String, Dict, Dict -> Http Response object #
def get(endpoint, headers = {}, data={}):
    return call_api(endpoint, "GET", headers, data)
    
    
    ##
# calls HTTP POST request to given endpoint with given data if any #
# String, Dict, Dict -> Http Response object #
def post(endpoint, headers = {}, data={}):
    return call_api(endpoint, "POST", headers, data)
 
##
# calls HTTP PUT request to given endpoint with given data if any #
# String, Dict, Dict -> Http Response object #
def put(endpoint, headers = {}, data={}):
    return call_api(endpoint, "PUT", headers, data)


# calls HTTP DELETE request to given endpoint with given data if any #
# String, Dict, Dict -> Http Response object #
def delete(endpoint, headers = {}, data={}):
    return call_api(endpoint, "DELETE", headers, data)

    
##
# get info about the user using the API currently #
# -> Http Response object #
def get_current_user():
    return get("https://api.spotify.com/v1/me").json()






# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================ AUTO EXECUTE CODE BELOW =============================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

# initialize token information to allow access to Spotify API
get_access_token()
print("Currently logged in to Spotify as " + get_current_user()["display_name"])

print(os.path.abspath(os.curdir))




# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================= Code Written by A-Dubs =============================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #