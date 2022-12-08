# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================== IMPORTS =====================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #

import random, string, json
from datetime import datetime, timedelta

# #==================================================================================================================# #
# #=============================================== MISC DB STUFF ===============================================# #
# #==================================================================================================================# #

def load() -> dict:
    with open("database.json", "r", encoding="utf-8") as db_file:
        db = json.loads(db_file.read())
    return db

def save(db : dict) -> None:
    with open("database.json", "w", encoding="utf-8") as db_file:
        json.dump(db, db_file, ensure_ascii=False, indent=4, default=str)

# convert spotify datetime timestamp string to python datetime object
# ex: "2022-10-10T21:28:01Z" 
# converts UTC -> EST
def sp_dt_to_py_dt(sp_datetime : str): 
    return datetime.strptime(sp_datetime, "%Y-%m-%dT%H:%M:%SZ")


# convert jukebox datetime timestamp string to python datetime object
# ex: "2022-10-12 13:51:45.734551"
# converts EST -> UTC 
def jb_dt_to_py_dt(jb_datetime : str):
    return datetime.strptime(jb_datetime, "%Y-%m-%d %H:%M:%S.%f") + timedelta(hours=4)

# #==================================================================================================================# #
# #=============================================== AUTH & TOKEN STUFF ===============================================# #
# #==================================================================================================================# #

# check if spotify token info exists
def sp_token_exists(sp_user_id : str):
    sp_user_id = str(sp_user_id)
    db = load()
    exists = False
    if not sp_user_id in db["users"]:
        db["users"][sp_user_id] = {}
        db["users"][sp_user_id]["sp_token"] = {}
        save(db)
        
    # user does exist
    else: 
        if not "sp_token" in db["users"][sp_user_id]:
            db["users"][sp_user_id]["sp_token"] = {}
            save(db)
        else:
            if "access_token" in (sp_token:=db["users"][sp_user_id]["sp_token"]) or "refresh_token" in sp_token:
                exists = True
    return exists

# store the sp_user_id and a random 'state' string to the database temporarily to help prevent man in the middle attacks
def cache_auth_code_random_state_string(sp_user_id : str):
    sp_user_id = str(sp_user_id)
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    print(random_chars)
    db = load()
    sp_token_exists(sp_user_id=sp_user_id)        
    db["users"][sp_user_id]["sp_token"]["auth_code_random_state_string"] = random_chars
    with open("database.json", "w", encoding="utf-8") as db_file:
        json.dump(db, db_file, ensure_ascii=False, indent=4, default=str)
    return random_chars

def get_sp_token_info(sp_user_id : str):
    sp_user_id = str(sp_user_id)
    db = load()
    if "expires_at" in db["users"][sp_user_id]["sp_token"]:
        db["users"][sp_user_id]["sp_token"]["expires_at"] = datetime.strptime(db["users"][sp_user_id]["sp_token"]["expires_at"], "%Y-%m-%d %H:%M:%S.%f")
    return db["users"][sp_user_id]["sp_token"]

def update_sp_token_info(access_token, refresh_token, expires_at, scope, sp_user_id : str):
    sp_user_id = str(sp_user_id)
    db = load()
    token=db["users"][sp_user_id]["sp_token"]
    token["access_token"] = access_token
    token["refresh_token"] = refresh_token
    token["expires_at"] = str(expires_at)
    token["scope"] = scope
    print("\n" + str(token) + "\n")
    save(db)
    return token


# #==================================================================================================================# #
# #===================================================== USERS ======================================================# #
# #==================================================================================================================# #

def add_jb_user(sp_user_id=None):
    load()
    if sp_user_id == None:
        list

# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #============================================= Code Written by a-dubs =============================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #
# #==================================================================================================================# #