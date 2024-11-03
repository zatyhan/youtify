from helpers import Processor, PlaylistMaker

yt_url = input('Enter youtube URL: ')
playlist_name = input('Enter playlist name: ')

try: 
    track = Processor(yt_url)
except:
    print('Invalid URL')
    raise SystemExit

try:
    track.process_url()
except:
    print('Failed to process track')
    raise SystemExit

playlist= PlaylistMaker(playlist_name)
start_time=0
video_length= track.video_length()

track_ids= set()
while start_time< video_length:
    try:
        isrc, track_title=  track.recognize_audio(start_time=start_time)
        print("Looking for: ", track_title)
        print(' ')
        track_id, found_title, duration= playlist.lookup(isrc)
        track_ids.add(track_id)
        print(f"Found: {found_title})")

        start_time+=duration +5

    except KeyboardInterrupt:
        print('The [Ctrl+C] key was pressed. Exiting...')
        raise SystemExit
    
    except Exception as e:
        print('Track not found')
        start_time+=60*2.5

    finally:
        print('\nFinding the next title...\n')
        
for t in track_ids:
    playlist.add_to_playlist(t)
print('Playlist created successfully!') 
        
    