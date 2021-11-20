import pandas as pd
import json
from googleapiclient import discovery as d, errors as e

import lib.youtube_channel as channel
import lib.upload_video as u
import lib.dataframe as dataframe
import lib.globals as g


def get_videos(env: str):
    f_path = g.video_file_in.format(env=env)
    videos = pd.read_excel(f_path, sheet_name=g.sheet_videos)
    return videos


def compare_videos(env: str, youtube: d.Resource):
    uploaded_videos = channel.get_channel_videos(youtube)
    uploaded_video_ids = []
    for video in uploaded_videos:
        uploaded_video_id = video['snippet']['resourceId']['videoId']
        uploaded_video_ids.append(uploaded_video_id)
    listed_video_ids = [v_id[-11:] for v_id in get_videos(env).NewYoutubeLink]
    if sorted(uploaded_video_ids) != sorted(listed_video_ids):
        missing_listed = set(listed_video_ids) - set(uploaded_video_ids)
        missing_uploaded = set(uploaded_video_ids) - set(listed_video_ids)
        if len(missing_listed) > 0:
            # '3ZNJBKJcwF8' duplicated in the youtube list
            # 'eZQdLW2cEOk' is missing from youtube list (actually it is there)
            if missing_listed != {'eZQdLW2cEOk'}:
                print(missing_listed)
                raise ValueError('Uploaded videos missing from the list!')
        if len(missing_uploaded) > 0:
            print(missing_uploaded)
            raise ValueError('Listed videos missing from youtube:')


def get_privacy_status(youtube: d.Resource, youtube_id: str):
    response = get_video_details(youtube=youtube, youtube_id=youtube_id,
                                 parts="status")
    status = response['items'][0]['status']['privacyStatus']
    return status


def get_youtube_id(video_id: int, env: str):
    videos = get_videos(env=env)
    link = videos.loc[videos.Id == video_id, 'NewYoutubeLink'].values[0]
    try:
        youtube_id = link.split('=')[1]
    except IndexError:
        raise ValueError(f'Cannot find youtube id in "{link}"')
    return youtube_id


def get_video_ids(videos: list):
    print(f"Get video ids for every video")
    video_ids = []
    for video in videos:
        video_ids.append(video['snippet']['resourceId']['videoId'])
    return video_ids


def get_video_details(youtube: d.Resource, youtube_id: str, parts="all",
                      export=False):
    parts_all = "contentDetails,fileDetails,id,liveStreamingDetails,"\
                "localizations,player,processingDetails,recordingDetails,"\
                "snippet,statistics,status,suggestions,topicDetails"
    request = youtube.videos().list(
        part=parts_all if parts == "all" else parts,
        id=youtube_id
    )
    response = request.execute()
    if export:
        with open(f'output/video_{youtube_id}.json', 'w') as outfile:
            json.dump(response, outfile)
    return response


def delete_video(youtube: d.Resource, video_id: str):
    print(f"Delete video: {video_id}")
    try:
        youtube.videos().delete(id=video_id).execute()
    except e.HttpError:
        print(f"Could not delete video {video_id}")


def get_markdown(video_id: int, env: str):
    videos = get_videos(env=env)
    link = videos.loc[videos.Id == video_id, 'NewYoutubeLink'].values[0]
    if pd.isna(link):
        return f"No markdown for #{video_id}"
    title = videos.loc[videos.Id == video_id, 'Title'].values[0]
    youtube_id = get_youtube_id(video_id=video_id, env=env)
    markdown = f'->[![{title}]' \
               f'(http://img.youtube.com/vi/{youtube_id}/0.jpg)]' \
               f'(http://www.youtube.com/watch?v={youtube_id} ' \
               f'"{title}")<-'
    return markdown


def get_video_description(video_data: pd.Series):
    desc = f'🔥 FELADAT GYAKORLÁSA: {video_data.ExerciseLink}\n' \
           f'🔥 Iratkozz fel a hírlevelünkre: ' \
           f'http://eepurl.com/hNOkz9\n' \
           f'🔥 Kövess minket Facebook-on: ' \
           f'https://www.facebook.com/groups/zsebtanar\n\n' \
           f'••••••••••••••••••••••••••••••••••••••••••••••••••••••\n\n' \
           f'💗 ️Tantárgy: Matematika\n' \
           f'💛 Osztály: 5. osztály\n' \
           f'💚 Témakör: {video_data.Topic}\n' \
           f'💙️ Feladat: {video_data.Exercise}\n\n' \
           f'••••••••••••••••••••••••••••••••••••••••••••••••••••••\n\n' \
           f'📝 Kérdés, észrevétel: info@zsebtanar.hu\n' \
           f'💻 Hivatalos honlap: https://www.zsebtanar.hu\n\n' \
           f'\n#zsebtanar #matematika'
    return desc


def get_video_title(video_data: pd.Series):
    video_title = f'{video_data.Title} | {video_data.Subject} - ' \
                  f'{video_data.Grade}'
    if len(video_title) > 100:
        raise ValueError(f'Title is too long: "{video_title}"\n'
                         f'It should be: "{video_title[0:99]}"')
    return video_title


def add_video(youtube: d.Resource, video_data: pd.Series, status='private'):
    print(f"Add video #{video_data.Id}")
    file_path = f'input/videos/{video_data.FileName}'
    video_title = get_video_title(video_data=video_data)
    description = get_video_description(video_data=video_data)
    youtube_link = u.upload_video(youtube=youtube,
                                  file=file_path,
                                  title=video_title,
                                  tags=video_data.Tags.split(','),
                                  description=description,
                                  privacy=status)
    return youtube_link


def add_videos(youtube: d.Resource, video_ids: list, env: str,
               status='private', delete_old=False):
    videos = get_videos(env=env)
    f_path = g.video_file_out.format(env=env)
    for index, video_data in videos[videos.Id.isin(video_ids)].iterrows():
        if delete_old and video_data.NewYoutubeLink:
            video_id = video_data.NewYoutubeLink.split('=')[1]
            delete_video(youtube=youtube, video_id=video_id)
        if delete_old or pd.isna(video_data.NewYoutubeLink):
            youtube_link = add_video(youtube=youtube, video_data=video_data,
                                     status=status)
            videos.loc[index, 'NewYoutubeLink'] = youtube_link
            dataframe.export_sheet(df=videos, sheet_name=g.sheet_videos,
                                   f_path=f_path)


def get_video_data(title: str, env: int):
    print(f'Find video data for "{title}"')
    videos = get_videos(env=env)
    video_data = videos[
        (videos['FileName'] == title) |
        (videos['Title'] == title)
    ]
    if len(video_data.index) == 0:
        raise ValueError(f'No match for "{title}"')
    elif len(video_data.index) > 1:
        raise ValueError(f'Multiple match for "{title}"')
    return video_data.iloc[0, :]


def update_videos(youtube: d.Resource, video_ids: list,
                  env: int, status='private'):
    videos = get_videos(env=env)
    for video_id in video_ids:
        print(f'Updating data for video #{video_id}')
        video_data = videos[videos.Id == video_id].iloc[0, ]
        video_title = get_video_title(video_data=video_data)
        video_description = get_video_description(video_data=video_data)
        if not pd.isna(video_data.NewYoutubeLink):
            youtube_id = video_data.NewYoutubeLink.split('/watch?v=')[1]
            request = youtube.videos().update(
                part="snippet,status",
                body={
                    "id": youtube_id,
                    "snippet": {
                        "title": video_title,
                        "description": video_description,
                        "tags": video_data.Tags.split(','),
                        "categoryId": 27
                    },
                    "status": {
                        "privacyStatus": status
                    }
                }
            )
            request.execute()
        else:
            raise ValueError(f'Youtube-link is missing!')
