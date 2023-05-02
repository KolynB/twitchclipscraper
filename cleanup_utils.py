import os
import glob

def cleanup_files(game_name, video_files, ending_video_file):
    for video_file in video_files:
        if os.path.exists(video_file) and video_file != ending_video_file:
            os.remove(video_file)

    # Remove the folders if they are empty
    for folder in os.listdir('tmp'):
        folder_path = os.path.join('tmp', folder)
        if os.path.isdir(folder_path) and not os.listdir(folder_path):
            os.rmdir(folder_path)