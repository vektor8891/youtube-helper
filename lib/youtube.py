import googleapiclient.discovery as d
import googleapiclient.errors as e
import googleapiclient.http as h
import pandas as pd
import lib.globals as g
import lib.upload_video as u
import lib.dataframe as dframe

VIDEOS = pd.read_excel(g.video_file, sheet_name=g.sheet_videos)
PLAYLISTS = pd.read_excel(g.video_file, sheet_name=g.sheet_playlists)


def print_channel_info(youtube: d.Resource):
    request = youtube.channels().list(part="snippet", mine=True)
    response = request.execute()
    channel_id = response['items'][0]['id']
    channel_name = response['items'][0]['snippet']['title']
    print(f'Channel info:\n\t- name: {channel_name}\n\t- id: {channel_id}')


def get_uploaded_videos(youtube: d.Resource):
    print(f"Get videos for my channel")
    request = youtube.channels().list(mine=True, part='contentDetails')
    uploads = request.execute()
    playlist_id = \
        uploads["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    uploaded_videos = []
    next_page_token = None
    while 1:
        res = youtube.playlistItems().list(playlistId=playlist_id,
                                           part='snippet',
                                           maxResults=50,
                                           pageToken=next_page_token).execute()
        uploaded_videos += res['items']
        next_page_token = res.get('nextPageToken')
        if next_page_token is None:
            break
    return uploaded_videos


def get_video_ids(videos: list):
    print(f"Get video ids for every video")
    video_ids = []
    for video in videos:
        video_ids.append(video['snippet']['resourceId']['videoId'])
    return video_ids


def delete_video(youtube: d.Resource, video_id: str):
    print(f"Delete video: {video_id}")
    try:
        youtube.videos().delete(id=video_id).execute()
    except e.HttpError:
        print(f"Could not delete video {video_id}")


def get_video_description(video_data: pd.Series):
    desc = f'FELADAT GYAKORLÁSA: {video_data.ExerciseLink}\n' \
           f'Tantárgy: Matematika 5. osztály\n' \
           f'Témakör: {video_data.Topic}\n' \
           f'Feladat: {video_data.Exercise.split(".")[1].strip()}\n\n' \
           f'Csatlakozz Facebook csoportjainkhoz!\n' \
           f'OKTATÓKNAK: https://www.fb.com/groups/597933901141678\n' \
           f'DIÁKOKNAK: https://www.fb.com/groups/197327654946239\n' \
           f'SZÜLŐKNEK: https://www.fb.com/groups/1570054486486347\n' \
           f'\n#zsebtanar #matematika'
    return desc


def get_video_title(video_data: pd.Series):
    video_title = f'{video_data.Title} | {video_data.Subject} - ' \
                  f'{video_data.Grade}🧐'
    return video_title


def add_video(youtube: d.Resource, video_data: pd.Series):
    print(f"Add video #{video_data.Id}")
    file_path = f'input/videos/{video_data.FileName}.mp4'
    video_title = get_video_title(video_data=video_data)
    description = get_video_description(video_data=video_data)
    youtube_link = u.upload_video(youtube=youtube,
                                  file=file_path,
                                  title=video_title,
                                  tags=video_data.Tags.split(','),
                                  description=description)
    return youtube_link


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


def add_videos(youtube: d.Resource, video_ids: list, delete_old=False):
    for index, video_data in VIDEOS[VIDEOS.Id.isin(video_ids)].iterrows():
        if delete_old and video_data.NewYoutubeLink:
            video_id = video_data.NewYoutubeLink.split('=')[1]
            delete_video(youtube=youtube, video_id=video_id)
        if delete_old or pd.isna(video_data.NewYoutubeLink):
            youtube_link = add_video(youtube=youtube, video_data=video_data)
            VIDEOS.loc[index, 'NewYoutubeLink'] = youtube_link
    dframe.export_sheet(df=VIDEOS, sheet_name=g.sheet_videos,
                        f_path=g.video_file)


def get_video_data(title: str):
    print(f'Find video data for "{title}"')
    video_data = VIDEOS[
        (VIDEOS['FileName'] == title) | (VIDEOS['Title'] == title)
        ]
    if len(video_data.index) == 0:
        raise ValueError(f'No match for "{title}"')
    elif len(video_data.index) > 1:
        raise ValueError(f'Multiple match for "{title}"')
    return video_data.iloc[0, :]


def update_video(youtube: d.Resource, video_ids: list):
    for video_id in video_ids:
        print(f'Updating data for video #{video_id}')
        video_data = VIDEOS[VIDEOS.Id == video_id].iloc[0, ]
        video_title = get_video_title(video_data=video_data)
        video_description = get_video_description(video_data=video_data)
        if not pd.isna(video_data.NewYoutubeLink):
            youtube_id = video_data.NewYoutubeLink.split('/watch?v=')[1]
            request = youtube.videos().update(
                part="snippet",
                body={
                    "id": youtube_id,
                    "snippet": {
                        "title": video_title,
                        "description": video_description,
                        "tags": video_data.Tags.split(','),
                        "categoryId": 27
                    }
                }
            )
            request.execute()
        else:
            raise ValueError(f'Youtube-link is missing!')


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


def rename_files():
    import os
    for index, row in VIDEOS.iterrows():
        os.rename(f'input/videos/{row.Title}.mp4',
                  f'input/videos/{row.FileName}.mp4')
