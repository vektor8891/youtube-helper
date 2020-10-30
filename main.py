import pandas as pd

import lib.auth as a
import lib.youtube_channel as channel
import lib.youtube_playlists as p
import lib.youtube_videos as v
import lib.globals as g
import lib.youtube_thumbnails as t
import lib.youtube_comments as c

client_id = 2
env = 'prod'  # test/prod
status = 'public'  # public/unlisted/private
create_new_connection = 1

conn = a.get_connection(create_new=create_new_connection, client_id=client_id)
channel.print_info(youtube=conn)

id_start = 41
id_end = 157
video_ids = list(range(id_start, id_end + 1))
# video_ids = [1]

# for video_id in video_ids:
#     print(v.get_markdown(video_id=video_id, env=env))

# v.add_videos(youtube=conn, video_ids=video_ids, status=status, env=env)
v.update_videos(youtube=conn, video_ids=video_ids, status=status, env=env)
# t.add_thumbnails(youtube=conn, video_ids=video_ids, env=env)
# p.add_videos_to_playlist(youtube=conn, video_ids=video_ids, env=env)
# c.add_comments(youtube=conn, video_ids=video_ids, env=env)

# for video_id in video_ids:
#     print(f'#{video_id}')
#     print(v.get_markdown(video_id=video_id, env=env))
