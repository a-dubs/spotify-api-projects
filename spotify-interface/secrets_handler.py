import base64

from itsdangerous import base64_decode, base64_encode
import json

redirect_uri_b64 = "aHR0cDovL2xvY2FsaG9zdDo1NjkxL2p1a2Vib3gvYXV0aA=="
client_id_b64 = "NDcyYjExNWY3YWY2NGMyYWExODNlMjI5ZGMyMTRlMjU="
client_secret_b64 = ""

# try to load client secret from file
try:
    with open("secret.txt","r",encoding="utf-8") as f:
        client_secret_b64 = (f.read())
except:
    print("Failed to load client secret from secret.txt!")

# if loading client secret from file failed, ask user for the client secret
if len(client_secret_b64) == 0:
    client_secret_b64 = base64_encode(input("Initilization required! Paste client secret: "))
    try:
        with open("secret.txt","w",encoding="utf-8") as f:
            f.write(client_secret_b64)
    except:
        print("Failed to write client secret to secrets.txt")

redirect_uri, client_id, client_secret = None, None, None

def decode_secrets():
    global redirect_uri, client_id, client_secret
    redirect_uri = base64_decode(bytes(redirect_uri_b64, encoding="utf-8")).decode(encoding="utf-8")
    client_id = base64_decode(bytes(client_id_b64, encoding="utf-8")).decode(encoding="utf-8")
    client_secret = base64_decode(bytes(client_secret_b64, encoding="utf-8")).decode(encoding="utf-8")
    return redirect_uri, client_id, client_secret

print("secrets:",decode_secrets())

