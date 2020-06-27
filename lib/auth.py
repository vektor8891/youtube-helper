import json

import google_auth_oauthlib.flow as f
import googleapiclient.discovery as d
import google.oauth2.credentials as c
from lib import globals as g


def get_credentials(create_new=False):
    credentials = create_credentials() if create_new else read_credentials()
    return credentials


def read_credentials():
    print(f'Reading credentials from {g.credentials_file}...')
    credentials = c.Credentials.from_authorized_user_file(g.credentials_file)
    return credentials


def create_credentials():
    print("Create credentials...")
    flow = f.InstalledAppFlow.from_client_secrets_file(
        g.client_secrets_file, g.scopes)
    credentials = flow.run_console()
    save_credentials(credentials=credentials)
    return credentials


def save_credentials(credentials):
    credentials_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    with open(g.credentials_file, 'w') as outfile:
        json.dump(credentials_data, outfile)
    print(f"Credentials saved to {g.credentials_file}.")


def get_api_connection():
    with open(g.api_file) as json_file:
        json_data = json.load(json_file)
        api_key = json_data[g.api_user]
    youtube = d.build('youtube', 'v3', developerKey=api_key)
    return youtube


def get_connection(create_new=False):
    credentials = get_credentials(create_new=create_new)
    youtube = d.build('youtube', 'v3', credentials=credentials)
    return youtube
