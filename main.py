import pandas as pd

import lib.auth as a
import lib.youtube_channel as channel
import lib.youtube_playlists as p
import lib.youtube_videos as v
import lib.globals as g
import lib.youtube_thumbnails as t
import lib.youtube_comments as c

client_id = 1
status = 'unlisted'

conn = a.get_connection(create_new=0, client_id=client_id)
channel.print_info(youtube=conn)

id_start = 1
id_end = 14
video_ids = list(range(id_start, id_end+1))
video_ids = [1]

v.add_videos(youtube=conn, video_ids=video_ids, status=status,
             delete_old=False, client_id=client_id)
v.update_videos(youtube=conn, video_ids=video_ids, status=status,
                client_id=client_id)
t.add_thumbnails(youtube=conn, video_ids=video_ids, client_id=client_id)
p.add_videos_to_playlist(youtube=conn, video_ids=video_ids,
                         client_id=client_id)
c.add_comments(youtube=conn, video_ids=video_ids, client_id=client_id)
