# youtube-helper

Python scripts to automatize tasks in Youtube Studio.

## Setup

1. Set up your Google API client ID using this [guide](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid)
2. Go to the [Google API Console](https://console.cloud.google.com/apis/credentials) and download the client ID in `*.json` format.
3. Save the file in the `private\client1` folder and rename it as `client_secrets.json`.
4. Open `main.py`, set `create_new_connection = 1` and run the file.
5. Sign in to Google and give permission to the app to manage your videos.
6. Copy the token and paste it in the terminal to save your credentials.
7. Set `create_new_connection = 0` in `main.py`.

If you need more clients (e.g. because you run out of your [quota](https://developers.google.com/youtube/v3/determine_quota_cost)):
1. Create a new project in the API Console. 
2. Create a new folder: `private\client2`.
3. Set `client_id = 2` in `main.py`.
4. Add a new client ID in the API Console and repeat the above steps for client 2.
