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


def create_playlists(youtube: d.Resource):
    playlists = get_playlists(youtube=youtube)
    for playlist_name in PLAYLISTS.PlaylistName.unique():
        if playlist_name not in playlists.keys():
            print(f'Create playlist "{playlist_name}"')
            body = {"snippet": {"title": playlist_name},
                    "status": {"privacyStatus": "public"}}
            youtube.playlists().insert(part='snippet,status',
                                       body=body).execute()


def remove_playlist_items(youtube: d.Resource):
    playlists = get_playlists(youtube=youtube)
    for playlist in playlists:
        playlist_filtered = PLAYLISTS[PLAYLISTS.PlaylistName == playlist]
        for index, row in playlist_filtered.iterrows():
            request = youtube.playlistItems().list(
                part="id",
                id=playlists[playlist]
            )
            response = request.execute()
            a = response['items']
            print(2)


def add_playlist_item(youtube: d.Resource, youtube_id: str,
                      playlist_id: str, position: int, name: str):
    print(f'Adding video #{youtube_id} to playlist "{name}" to position '
          f'{position}')
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


def add_playlist_items(youtube: d.Resource):
    playlists = get_playlists(youtube=youtube)
    for name in PLAYLISTS.Name.unique():
        for index, row in PLAYLISTS[PLAYLISTS.Name == name].iterrows():
            title = f'{row.Name} | {row.Subject} {row.Grade}'
            playlist_id = playlists[title]
            youtube_id = row.YoutubeLink.split('=')[1]
            add_playlist_item(youtube=youtube, youtube_id=youtube_id,
                              playlist_id=playlist_id, name=name,
                              position=row.Position)


def update_playlists(youtube: d.Resource, delete_existing=False):
    delete_playlists(youtube=youtube, delete_existing=delete_existing)
    create_playlists(youtube=youtube)
    remove_playlist_items(youtube=youtube)
    add_playlist_items(youtube=youtube)
    print(2)
