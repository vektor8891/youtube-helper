import lib.auth
import lib.youtube

# lib.youtube.rename_files()
conn = lib.auth.get_connection(create_new=0)
lib.youtube.print_channel_info(youtube=conn)
videos = lib.youtube.get_videos(youtube=conn)
# video_ids = lib.youtube.get_video_ids(videos=videos)
# video_id = 'VssCFbPkd2I'
# lib.youtube.delete_video(youtube=conn, video_id=video_ids[0])
lib.youtube.add_videos(youtube=conn, video_ids=[7, 8, 9], delete_old=False)
lib.youtube.update_video(youtube=conn, videos=videos)
print()
