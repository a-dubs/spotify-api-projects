from spotify_interface import *

playlists = get_playlists(sp_user_id="0")

blend_pl = [pl for pl in playlists if pl.id == "37i9dQZF1EJHYPTpq3GrTO"][0] 
blend_pl.get_tracks()

history_pl = [pl for pl in playlists if "Helen & Alec's Blend History".lower() in pl.name.lower()][0] 

history_pl.add_tracks(blend_pl.tracks)

history_pl.get_tracks()

print(", ".join([track.__dict__["name"] for track in history_pl.tracks]))
