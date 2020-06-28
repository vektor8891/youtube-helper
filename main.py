import lib.auth
import lib.youtube

# conn_api = lib.auth.get_api_connection()
conn = lib.auth.get_connection(create_new=0)
# channel_id = lib.youtube.get_channel_id(youtube=conn)
# channel_id = 'UC8aqu8qcioAPG_BTMskAcmA'  # zsebtanar
# channel_id = 'UCdqFGivUuQyEKh06RZLsReg'  # teszt
# videos = lib.youtube.get_videos(youtube=conn_api, channel_id=channel_id)
# video_ids = lib.youtube.get_video_ids(youtube=conn_api,
# channel_id=channel_id)
# video_id = 'VssCFbPkd2I'
# lib.youtube.delete_video(youtube=conn, video_id=video_ids[0])
lib.youtube.add_videos(youtube=conn, video_ids=[1, 2, 3], delete_old=True)
print()
