import googleapiclient.discovery as d


def print_channel_info(youtube: d.Resource):
    request = youtube.channels().list(part="snippet", mine=True)
    response = request.execute()
    channel_id = response['items'][0]['id']
    channel_name = response['items'][0]['snippet']['title']
    print(f'Channel info:\n\t- name: {channel_name}\n\t- id: {channel_id}')


def get_channel_videos(youtube: d.Resource):
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
