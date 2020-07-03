import pandas as pd

import lib.auth as a
import lib.youtube_channel as c
import lib.youtube_playlists as p
import lib.youtube_videos as v
import lib.globals as g
import lib.youtube_thumbnails as t

g.client_id = 1
video_ids = list(range(1, 11))
video_ids = [10, 11]

conn = a.get_connection(create_new=0)
c.print_channel_info(youtube=conn)
# v.add_videos(youtube=conn, video_ids=video_ids, delete_old=False)
# v.update_video(youtube=conn, video_ids=video_ids)
# t.add_thumbnails(youtube=conn, video_ids=video_ids)
p.add_videos_to_playlist(youtube=conn, video_ids=video_ids)
