import pickle
import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload


#google auth service for upload purposes
def get_authenticated_service():
    credentials = None
    client_secrets_file = 'client_secret.json'
    credentials_file = 'credentials.pickle'
    scopes = ['https://www.googleapis.com/auth/youtube.upload']

    if os.path.exists(credentials_file):
        with open(credentials_file, 'rb') as file:
            credentials = pickle.load(file)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(google.auth.transport.requests.Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            credentials = flow.run_local_server(port=8080) # Use port=0 to select an available port automatically

        with open(credentials_file, 'wb') as file:
            pickle.dump(credentials, file)

    return googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)

#allows upload to youtube.  videos will be stuck private.
def upload_video(youtube, video_file, title, description, tags, category_id):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "unlisted" #privacy status
        }
    }

    media_body = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media_body)
    response = None

    while response is None:
        status, response = request.next_chunk()
        if response is not None:
            if "id" in response:
                print(f"Video uploaded successfully: https://www.youtube.com/watch?v={response['id']}")
            else:
                print("Error uploading the video")

    return response
