import pandas as pd
from googleapiclient import discovery as d, http as h

import lib.youtube_videos


def download_thumbnails():
    import requests
    import shutil
    df_videos = lib.youtube_videos.get_videos()
    for index, row in df_videos.iterrows():
        yt_id = row.OldYoutubeLink.split('/')[3]
        image_url = f"https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg"
        resp = requests.get(image_url, stream=True)
        local_file = open(f'input/thumbnails/{row.Id}.jpg', 'wb')
        resp.raw.decode_content = True
        shutil.copyfileobj(resp.raw, local_file)
        del resp
        print()


def add_thumbnails(youtube: d.Resource, video_ids: list):
    df_videos = lib.youtube_videos.get_videos()
    for video_id in video_ids:
        print(f'Adding thumbnail for video #{video_id}')
        thumbnail_img = f"input/thumbnails/{video_id}.jpg"
        link = df_videos.loc[df_videos.Id == video_id,
                             'NewYoutubeLink'].values[0]
        if not pd.isna(link):
            youtube_id = link.split('/watch?v=')[1]
            request = youtube.thumbnails().set(
                videoId=youtube_id,
                media_body=h.MediaFileUpload(thumbnail_img)
            )
            request.execute()
        else:
            raise ValueError(f'Youtube-link is missing!')
