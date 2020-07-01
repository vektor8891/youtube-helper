import lib.auth
import lib.youtube

# lib.youtube.download_thumbnails()
conn = lib.auth.get_connection(create_new=0)
# lib.youtube.print_channel_info(youtube=conn)
# videos = lib.youtube.get_videos(youtube=conn)
video_ids = [7, 8, 9]
# lib.youtube.add_videos(youtube=conn, video_ids=video_ids, delete_old=False)
# lib.youtube.update_video(youtube=conn, video_ids=video_ids)
lib.youtube.add_thumbnails(youtube=conn, video_ids=video_ids)
print()
