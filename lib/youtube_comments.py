import googleapiclient.discovery as d
import json
import pandas as pd

import lib.youtube_videos as v
import lib.youtube_channel as channel
import lib.globals as g
import lib.dataframe as dframe


def get_video_comments(youtube: d.Resource, video_id: int, export=False):
    youtube_id = v.get_youtube_id(video_id=video_id)
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=youtube_id
    )
    response = request.execute()
    channel_id = channel.get_id(youtube=youtube)
    if export:
        with open(f'output/comment_{youtube_id}.json', 'w') as outfile:
            json.dump(response, outfile)
    for comment in response['items']:
        top_comment = comment['snippet']['topLevelComment']
        author_id = top_comment['snippet']['authorChannelId']['value']
        if author_id == channel_id:
            return comment
    return response


def get_comment_text(video_data: pd.DataFrame):
    comment = f'➡️FELADAT GYAKORLÁSA: {video_data.ExerciseLink}\n' \
              f'➡️Még több feladat: https://www.zsebtanar.hu'
    return comment


def add_comment(youtube: d.Resource, youtube_id: str, comment_text: str):
    request = youtube.commentThreads().insert(
        part='snippet',
        body={
            "snippet": {
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment_text
                    }
                },
                "videoId": youtube_id
            }
        }
    )
    response = request.execute()
    return response['id']


def update_comment(youtube: d.Resource, comment_id: str, comment_text: str):
    request = youtube.commentThreads().update(
        part='snippet',
        body={
            "id": comment_id,
            "snippet": {
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment_text
                    }
                }
            }
        }
    )
    response = request.execute()
    return response


def add_comments(youtube: d.Resource, video_ids: list, client_id: int):
    videos = v.get_videos(client_id=client_id)
    for index, row in videos[videos.Id.isin(video_ids)].iterrows():
        comment_text = get_comment_text(video_data=row)
        youtube_id = v.get_youtube_id(video_id=row.Id, client_id=client_id)
        status = v.get_privacy_status(youtube=youtube, youtube_id=youtube_id)
        if status == 'private':
            raise ValueError('Cannot add comment to private video!')
        if not pd.isna(row.CommentId):
            print(f'Updating comment for video #{row.Id}')
            update_comment(youtube=youtube, comment_id=row.CommentId,
                           comment_text=comment_text)
        else:
            print(f'Adding comment for video #{row.Id}')
            comment_id = add_comment(youtube=youtube, youtube_id=youtube_id,
                                     comment_text=comment_text)
            videos.loc[index, 'CommentId'] = comment_id
    f_path = g.video_file.format(client_id=client_id)
    dframe.export_sheet(df=videos, sheet_name=g.sheet_videos, f_path=f_path)
