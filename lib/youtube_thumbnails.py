import pandas as pd
from googleapiclient import discovery as d, http as h

import lib.youtube_videos


def add_thumbnails(youtube: d.Resource, video_ids: list, client_id: int):
    df_videos = lib.youtube_videos.get_videos(client_id=client_id)
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
