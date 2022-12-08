from flask import Flask
from flask import request as req
from threading import Thread
import json
import os


os.chdir(os.path.dirname(os.path.realpath(__file__)))
api = Flask(__name__)

@api.route('/spotify/auth')
def jukebox_auth_endpoint():
    with open("database.json", "r", encoding="utf-8") as db_file:
        db = json.loads(db_file.read())
    code = req.args.get("code")
    if len(req.args.get("state").split(":")) != 2 :
        return "bad state value..."
    state_str, sp_user_id = req.args.get("state").split(":")
    if state_str != db["users"][sp_user_id]["sp_token"]["auth_code_random_state_string"]:
        return "bad state value..."
    print(f"sp_user_id:{sp_user_id} ; code:{code}")
    db["users"][sp_user_id]["sp_token"]["code"] = code
    db["users"][sp_user_id]["sp_token"]["auth_code_random_state_string"] = ""
    with open("database.json", "w", encoding="utf-8") as db_file:
        json.dump(db, db_file, ensure_ascii=False, indent=4, default=str)

    return "Authentication Code succesfully retrieved! You may close this page now." if code else "CODE FAILED TO BE RETRIEVED :("

# Thread(target= lambda : api.run(port=5691, use_reloader=False)).start()
api.run(port=5691)