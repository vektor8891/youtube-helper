import pandas as pd
from googleapiclient import discovery as d

from lib import globals as g

PLAYLISTS = pd.read_excel(g.video_file, sheet_name=g.sheet_playlists)


def get_playlists(youtube: d.Resource):
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


def delete_playlists(youtube: d.Resource, delete_existing=False):
    playlists = get_playlists(youtube=youtube)
    for playlist in playlists.keys():
        if playlist not in PLAYLISTS.PlaylistName.unique() or delete_existing:
            print(f'Delete playlist "{playlist}"')
            youtube.playlists().delete(id=playlists[playlist]).execute()


def insert_playlist_item(youtube: d.Resource, youtube_id: str,
                         playlist_id: str, position: int):
    print(f'Inserting video #{youtube_id} into playlist #{playlist_id} at '
          f'position {position}')
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


def add_video_to_playlist(youtube: d.Resource, video_id: int):
    playlists = get_playlists(youtube=youtube)
    playlists_filt = PLAYLISTS[PLAYLISTS.VideoId == video_id]
    for index, row in playlists_filt.iterrows():
        print(f'Adding video #{video_id} to playlist {row.PlaylistName}')
        youtube_id = row.YoutubeLink.split('=')[1]
        if row.PlaylistName not in playlists.keys():
            raise ValueError(f'Playlist "{row.PlaylistName}" not found! '
                             f'Please create it manually.')
        else:
            playlist_id = playlists[row.PlaylistName]
        insert_playlist_item(youtube=youtube, youtube_id=youtube_id,
                             playlist_id=playlist_id, position=row.Position)


def add_videos_to_playlist(youtube: d.Resource, video_ids: list):
    for video_id in video_ids:
        add_video_to_playlist(youtube=youtube, video_id=video_id)
