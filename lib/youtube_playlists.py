import pandas as pd
from googleapiclient import discovery as d

import lib.globals as g
import lib.youtube_videos as v


def get_youtube_playlists(youtube: d.Resource):
    playlists = {}
    request = youtube.playlists().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=25
    )
    response = request.execute()
    for item in response['items']:
        title = item['snippet']['title']
        playlists[title] = item['id']
    return playlists


def get_playlist_data(client_id: int):
    f_path = g.video_file.format(client_id=client_id)
    playlists = pd.read_excel(f_path, sheet_name=g.sheet_playlists)
    playlists['PlaylistName'] = playlists.apply(
        lambda x: f"{x.Name} | {x.Subject} {x.Grade}",
        axis=1
    )
    return playlists


def insert_playlist_item(youtube: d.Resource, youtube_id: str,
                         playlist_id: str, position: int):
    print(f'Inserting #{youtube_id} into playlist at position {position}')
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "position": position,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": youtube_id
                }
            }
        }
    )
    response = request.execute()
    return response


def add_video_to_playlist(youtube: d.Resource, video_id: int, client_id: int):
    playlists = get_youtube_playlists(youtube=youtube)
    df_playlists = get_playlist_data(client_id=client_id)
    playlists_filt = df_playlists[df_playlists.VideoId == video_id]
    for index, row in playlists_filt.iterrows():
        print(f'Adding video #{video_id} to playlist "{row.PlaylistName}"')
        youtube_id = v.get_youtube_id(video_id=video_id, client_id=client_id)
        if row.PlaylistName not in playlists.keys():
            raise ValueError(f'Playlist "{row.PlaylistName}" not found! '
                             f'Please create it manually.')
        else:
            playlist_id = playlists[row.PlaylistName]
        insert_playlist_item(youtube=youtube, youtube_id=youtube_id,
                             playlist_id=playlist_id, position=row.Position)


def add_videos_to_playlist(youtube: d.Resource, video_ids: list,
                           client_id: int):
    for video_id in video_ids:
        add_video_to_playlist(youtube=youtube, video_id=video_id,
                              client_id=client_id)
