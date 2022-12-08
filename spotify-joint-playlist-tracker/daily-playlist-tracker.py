from time import strftime
from spotify_interface import *
from pprint import pprint 

playlists = get_playlists(sp_user_id="0")
pl = [pl for pl in playlists if "Known to man".lower() in pl.name.lower()][0] 
print()
pprint(pl.__dict__)
print()
pl_tracks = pl.get_tracks()
print("\n"+", ".join([t.name for t in pl_tracks])+"\n")

def group_pl_tracks_by_who_added(pl_tracks : list[PlaylistTrack]):
    grouped_tracks = {
        # SpotfiyUser.id : list[PlaylistTrack] 
    }
    for plt in pl_tracks:
        if not plt.added_by.id in grouped_tracks:
            grouped_tracks[plt.added_by.id] = []
        grouped_tracks[plt.added_by.id].append(plt)
    return grouped_tracks
pprint(group_pl_tracks_by_who_added(pl_tracks))

def utcdt_to_estdt(utcdt: datetime) -> datetime:
    return (utcdt - timedelta(hours=4))
    
def dt_to_dts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d") 

def dts_to_dt(dts: str) -> datetime:
    return datetime.strptime(dts,"%Y-%m-%d")

def inc_dts(dts : str, n=1) -> str:
    return dt_to_dts(dts_to_dt(dts) + timedelta(days=n))

def dec_dts(dts : str, n=1) -> str:
    return dt_to_dts(dts_to_dt(dts) - timedelta(days=n))


def group_by_date(pl_tracks : list[PlaylistTrack]):
    for plt in pl_tracks:
        plt.added_at = utcdt_to_estdt(plt.added_at)
    
    today_dts = dt_to_dts(utcdt_to_estdt(datetime.utcnow()))

    tracks_by_user = group_pl_tracks_by_who_added(pl_tracks=pl_tracks)
    tracks_by_date = {}
    dts_it = dt_to_dts(pl_tracks[0].added_at)
    while dts_it != dt_to_dts(utcdt_to_estdt(datetime.utcnow())+timedelta(days=1)):
        tracks_by_date[dts_it] = {id : [] for id in tracks_by_user}
        dts_it = inc_dts(dts_it)
    # earliest_date = ts[list(ts.keys)[0]][0].added_at
    
    for dts in tracks_by_date:
        tracks_by_date[dts] = {id : [t for t in tracks_by_user[id] if dts == dt_to_dts(t.added_at)] for id in tracks_by_user}
    # tracks_added = {id:len(tracks_by_user[id]) for id in tracks_by_user}
    num_tracks_added = {id:0 for id in tracks_by_user}
    ids = [id for id in tracks_by_user]
    u1 = ids[0]
    u2 = ids[1]
    
    for dts in tracks_by_date:
        # input()
        diff = 0
        pprint(tracks_by_date)
        print(dts)
        num_tracks_added[u1] += (n1_added:=len(tracks_by_date[dts][u1]))
        num_tracks_added[u2] += (n2_added:=len(tracks_by_date[dts][u2]))
        print(n1_added, n2_added)
        # if (n1:=num_tracks_added[u1]) < (n2:=num_tracks_added[u2]) or n2_added == 0:
        if n1_added == 0 and dts != today_dts:
            steal_from_dts = dts
            while True:
                steal_from_dts = inc_dts(steal_from_dts)
                if steal_from_dts > today_dts:
                    print("Oh uh, no time travel into the future allowed!")
                    break
                if len(tracks_by_date[steal_from_dts][u1]) == 0:
                    print("Uh oh! no tracks to steal from "+ steal_from_dts)
                else:
                    tracks_by_date[dts][u1].append(tracks_by_date[steal_from_dts][u1][0])
                    tracks_by_date[steal_from_dts][u1] = tracks_by_date[steal_from_dts][u1][1:]
                    num_tracks_added[u1] += 1
                    break
                # multiple missing, not just one - more complex:
                # diff = n2 - n1
                # while diff > 0:
                #     steal_from_dts = inc_dts()
                #     num_to_steal = min(len(tracks_by_date[steal_from_dts][u1]),diff)
                #     tracks_by_date[steal_from_dts][u1] = tracks_by_date[steal_from_dts][u1][num_to_steal:]
        elif n1_added == 2:
            add_to_dts = inc_dts(dts)
            # if not add_to_dts in tracks_by_date: # this check is not needed for now
            tracks_by_date[add_to_dts][u1].append(tracks_by_date[dts][u1][-1])
            tracks_by_date[dts][u1] = tracks_by_date[dts][u1][:-1]
            num_tracks_added[u1] -= 1

        if n2_added == 0 and dts != today_dts:
            steal_from_dts = dts
            while True:
                steal_from_dts = inc_dts(steal_from_dts)
                if steal_from_dts > today_dts:
                    print("Oh uh, no time travel into the future allowed!")
                    break
                if len(tracks_by_date[steal_from_dts][u2]) == 0:
                    print("Uh oh! no tracks to steal from "+ steal_from_dts)
                else:
                    tracks_by_date[dts][u2].append(tracks_by_date[steal_from_dts][u2][0])
                    tracks_by_date[steal_from_dts][u2] = tracks_by_date[steal_from_dts][u2][1:]
                    num_tracks_added[u2] += 1
                    break
            # diff = n1 - n2
        # if (n1:=num_tracks_added[u1]) > (n2:=num_tracks_added[u2]) or n1_added == 0:
        elif n2_added == 2:
            add_to_dts = inc_dts(dts)
            # if not add_to_dts in tracks_by_date: # this check is not needed for now
            tracks_by_date[add_to_dts][u2].append(tracks_by_date[dts][u2][-1])
            tracks_by_date[dts][u2] = tracks_by_date[dts][u2][:-1]
            num_tracks_added[u2] -= 1        
        
    return tracks_by_date

def get_num_days_behind(tracks_by_date : dict[str, dict[str,str]]):
    u1, u2 = list(list(tracks_by_date.values())[0].keys())
    print("Number of days behind:")
    u1_days_behind = [dts for dts in tracks_by_date if len(tracks_by_date[dts][u1]) == 0]     
    u2_days_behind = [dts for dts in tracks_by_date if len(tracks_by_date[dts][u2]) == 0]     
    print(f"{u1} - {len(u1_days_behind)} days behind (counting today's song)")            
    print(f"{u2} - {len(u2_days_behind)} days behind (counting today's song)")    

pprint(tracks_per_day:=group_by_date(pl_tracks))
get_num_days_behind(tracks_per_day)

def export_pt(pt: PlaylistTrack) -> dict[str,str]:
    return {
        "id" : pt.id,
        "name" : pt.name,
        "artists" : pt.artists_str,
        "images" : pt.images
    }

output = {}
for dts in tracks_per_day:
    output[dts] = {id:[export_pt(pt) for pt in tracks_per_day[dts][id]] for id in tracks_per_day[dts]}

print(output)
with open("processed_tracks_added_per_day.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(output))

