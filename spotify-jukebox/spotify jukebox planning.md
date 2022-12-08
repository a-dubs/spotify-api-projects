
3 different user types/scopes:
 - a "listener", who will log in with their spotify account credentials and their spotify queue and currently playing
   track will be controlled via the API
 - a "member", who will log in with their spotify account credentials so they can look at their own playlists and songs
   to make adding and finding songs easier. 
   - this user can then easily be switched to a "listener" and vice-versa
 - a "guest", who will 

<br>

 - first person creates a session, which will be given a unique id 
   - (maybe use seconds since epoch + user's spotify id? or just use an auto incremented id)

 - each session will store the queue in the jukebox's backend as to not rely on spotify's queue
   - each listener's spotify will actually have no queue, because this queue cannot be retrieved via the api
   - the queue will be preserved as a list such that any songs that were previously listened to can be rewinded too
     unlike the normal spotify queue functionality
   - thus, in order to "skip" to the next or prev song, the relevant song will be added to the user's playback queue
     then immediately following, the relevant skip() api call will be made
   - similarly, when the queue is being naturally progressed through (i.e. song ends then next song plays), the player
     will monitor the state of playback and once the song gets within the final 3(?) seconds, the next song in the
     jukebox's list will be added



in UI timeline view of queue, allow for scrolling back in time to like "greyed out" / "disabled" versions of the tiles /
list entries so that you can see what was played before and have a "re-add to queue" button that will create a new queue
entry at the bottom of the jukebox's list

add spotify embed so that users can hear a sample of the song ?