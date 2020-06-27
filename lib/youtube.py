import googleapiclient.discovery as d


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
    request = youtube.videos().delete(
        id=video_id
    )
    request.execute()
