import pandas as pd
from googleapiclient import discovery as d, http as h

from lib.youtube_videos import VIDEOS


def download_thumbnails():
    import requests
    import shutil
    for index, row in VIDEOS.iterrows():
        yt_id = row.OldYoutubeLink.split('/')[3]
        image_url = f"https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg"
        resp = requests.get(image_url, stream=True)
        local_file = open(f'input/thumbnails/{row.Id}.jpg', 'wb')
        resp.raw.decode_content = True
        shutil.copyfileobj(resp.raw, local_file)
        del resp
        print()


def add_thumbnails(youtube: d.Resource, video_ids: list):
    for video_id in video_ids:
        print(f'Adding thumbnail for video #{video_id}')
        thumbnail_img = f"input/thumbnails/{video_id}.jpg"
        link = VIDEOS.loc[VIDEOS.Id == video_id, 'NewYoutubeLink'].values[0]
        if not pd.isna(link):
            youtube_id = link.split('/watch?v=')[1]
            request = youtube.thumbnails().set(
                videoId=youtube_id,
                media_body=h.MediaFileUpload(thumbnail_img)
            )
            request.execute()
        else:
            raise ValueError(f'Youtube-link is missing!')