import googleapiclient.discovery as d
import googleapiclient.errors as e
import pandas as pd
import lib.globals as g
import lib.upload_video as u
import io


def get_channel_id(youtube: d.Resource):
    request = youtube.channels().list(part="id", mine=True)
    response = request.execute()
    channel_id = response['items'][0]['id']
    return channel_id


def get_videos(youtube: d.Resource, channel_id: str):
    print(f"Get videos for channel: {channel_id}")
    request = youtube.channels().list(id=channel_id, part='contentDetails')
    uploads = request.execute()
    playlist_id = \
        uploads["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    videos = []
    next_page_token = None
    while 1:
        res = youtube.playlistItems().list(playlistId=playlist_id,
                                           part='snippet',
                                           maxResults=50,
                                           pageToken=next_page_token).execute()
        videos += res['items']
        next_page_token = res.get('nextPageToken')
        if next_page_token is None:
            break
    return videos


def get_video_ids(youtube: d.Resource, channel_id: str):
    print(f"Get video ids for every video in channel {channel_id}")
    videos = get_videos(youtube=youtube, channel_id=channel_id)
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
    description = f'FELADAT GYAKORLÁSA: {video_data.ExerciseLink}\n' \
                  f'Tantárgy: Matematika 5. osztály\n' \
                  f'Témakör: {video_data.Topic}\n' \
                  f'Feladat: {video_data.Exercise.split(".")[1].strip()}\n\n' \
                  f'Csatlakozz Facebook csoportjainkhoz!\n' \
                  f'OKTATÓKNAK: https://www.fb.com/groups/597933901141678\n' \
                  f'DIÁKOKNAK: https://www.fb.com/groups/197327654946239\n' \
                  f'SZÜLŐKNEK: https://www.fb.com/groups/1570054486486347\n' \
                  f'\n#zsebtanar #matematika'
    return description


def add_video(youtube: d.Resource, video_data: pd.Series):
    print(f"Add video #{video_data.Id}")
    file_path = f'input/videos/{video_data.Title}.mp4'
    video_title = f'{video_data.Title} | {video_data.Subject} - ' \
                  f'{video_data.Grade}'
    description = get_video_description(video_data=video_data)
    youtube_link = u.upload_video(youtube=youtube,
                                  file=file_path,
                                  title=video_title,
                                  tags=video_data.Tags.split(','),
                                  description=description)
    return youtube_link


def add_videos(youtube: d.Resource, video_ids: list, delete_old=False):
    videos = pd.read_excel(g.video_file)
    for index, video_data in videos[videos.Id.isin(video_ids)].iterrows():
        if delete_old and video_data.NewYoutubeLink:
            video_id = video_data.NewYoutubeLink.split('=')[1]
            delete_video(youtube=youtube, video_id=video_id)
        if delete_old or not video_data.NewYoutubeLink:
            youtube_link = add_video(youtube=youtube, video_data=video_data)
        videos.loc[index, 'NewYoutubeLink'] = youtube_link
    videos.to_excel(g.video_file, index=False)
    return 2
