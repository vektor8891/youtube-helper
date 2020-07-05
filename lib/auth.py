import json

import google_auth_oauthlib.flow as f
import googleapiclient.discovery as d
import google.oauth2.credentials as c
from lib import globals as g


def get_credentials(client_id: int, create_new=False):
    if create_new:
        credentials = create_credentials(client_id=client_id)
    else:
        credentials = read_credentials(client_id=client_id)
    return credentials


def read_credentials(client_id: int):
    f_path = g.credentials_file.format(client_id=client_id)
    print(f'Reading credentials from {f_path}...')
    credentials = c.Credentials.from_authorized_user_file(f_path)
    return credentials


def create_credentials(client_id: int):
    print(f"Create credentials for client #{client_id}...")
    f_path = g.client_secrets_file.format(client_id=client_id)
    flow = f.InstalledAppFlow.from_client_secrets_file(f_path, g.scopes)
    credentials = flow.run_console()
    save_credentials(credentials=credentials, client_id=client_id)
    return credentials


def save_credentials(credentials, client_id: int):
    credentials_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.env,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    f_path = g.credentials_file.format(client_id=client_id)
    with open(f_path, 'w') as outfile:
        json.dump(credentials_data, outfile)
    print(f"Credentials saved to {f_path}.")


def get_api_connection():
    with open(g.api_file) as json_file:
        json_data = json.load(json_file)
        api_key = json_data[g.api_user]
    youtube = d.build('youtube', 'v3', developerKey=api_key)
    return youtube


def get_connection(client_id: int, create_new=False):
    credentials = get_credentials(create_new=create_new, client_id=client_id)
    youtube = d.build('youtube', 'v3', credentials=credentials)
    return youtube
