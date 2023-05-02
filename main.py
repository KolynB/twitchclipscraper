import sys
import argparse
from datetime import datetime, date
import os
from api_utils import get_access_token, get_game_id, get_top_clips, get_broadcaster_login
from video_utils import download_clip, add_text_to_video, concatenate_videos
from youtube_utils import get_authenticated_service, upload_video
from cleanup_utils import cleanup_files
from settings import client_id, client_secret, SCOPES, working_directory, basepath

# Argument parsing
parser = argparse.ArgumentParser(description='Scrape top Twitch clips')
parser.add_argument('-g', '--game', type=str, required=True, help='Name of the game')
parser.add_argument('-d', '--directory', type=str, default='./data', help='Path to the working directory')
parser.add_argument('-b', '--basepath', type=str, default='', help='Base path for downloading files (useful for remote servers)')
args = parser.parse_args()

game_name = args.game.lower()
basepath = f'PATH_TO_FOLDER/tmp/{game_name}/'


def main():
    # Set the working directory
    if not os.path.exists(working_directory):
        os.makedirs(working_directory)

    os.chdir(working_directory)
    
    # Main script
    access_token = get_access_token(client_id, client_secret)
    game_id = get_game_id(game_name, client_id, access_token)
    top_clips = get_top_clips(game_id, client_id, access_token)

    if not os.path.exists(basepath):
        os.makedirs(basepath)

    
    video_files = []
    unique_channels = set()

    os.makedirs(basepath, exist_ok=True)


    with open(os.path.join(basepath, 'channels.txt'), 'w') as channels_file:

        for idx, clip in enumerate(top_clips, start=1):
            broadcaster_login = get_broadcaster_login(clip['broadcaster_id'], client_id, access_token)
            channel_url = f"{broadcaster_login}"
            print(f"Downloading clip {clip['id']} - {clip['title']} from channel {channel_url}")
            download_clip(clip, basepath, game_name)
            print(f"Downloaded clip {clip['id']} - {clip['title']} from channel {channel_url}")

            unique_channels.add(channel_url)

            # Add text to the video
            input_file = os.path.join(basepath, f"{clip['id']}.mp4")
            output_file = os.path.join(basepath, f"{idx:02d}_{args.game}_{broadcaster_login}.mp4")
            #font file path can be changed
            font_file = 'C\\\\:/Windows/fonts/impact.ttf'
            add_text_to_video(input_file, output_file, broadcaster_login, font_file)

            video_files.append(output_file)

            # Remove the original video file
            os.remove(input_file)

        for channel_url in unique_channels:
            channels_file.write(channel_url + '\n')

    game_videos = {
        'valorant': 'PATH_TO_OUTRO_VIDEO.mp4',
        'overwatch 2': 'PATH_TO_OUTRO_VIDEO.mp4',
        # Add more games and their video paths here
    }

    # Set the default ending video file
    default_ending_video = 'PATH_TO_DEFAULT_OUTRO_VIDEO.mp4'

    # Select the ending video for the current game
    ending_video_file = game_videos.get(game_name, default_ending_video)

    today = date.today().strftime('%Y%m%d')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    combined_output_file = os.path.join(basepath, f"{game_name}_DailyClips_{today}_{timestamp}.mp4")
    concatenate_videos(video_files, combined_output_file, image_video_file=ending_video_file)



    # Cleanup downloaded and intermediate files
    cleanup_files(game_name, video_files, ending_video_file)

    youtube = get_authenticated_service()
    title = f"{game_name}_DailyClips_{datetime.now().strftime('%Y%m%d')}"
    description = f"{game_name} Daily Highlights #"

    tags = ["gaming", "twitch", "highlights", "daily", "montage", game_name]
    category_id = "20"  # Gaming category

    #upload_video(youtube, combined_output_file, title, description, tags, category_id)

if __name__ == "__main__":
    main()
