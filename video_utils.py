import os
import urllib.request
import subprocess
import sys

#download clips
def download_clip(clip, basepath, game_name):
    thumb_url = clip['thumbnail_url']
    mp4_url = clip['thumbnail_url'].split("-preview", 1)[0] + ".mp4"
    out_filename = clip['id'] + ".mp4"
    output_path = (basepath + out_filename)

    def dl_progress(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write("\r...%d%%" % percent)
        sys.stdout.flush()

    if not os.path.exists(basepath):
        os.makedirs(basepath)

    try:
        urllib.request.urlretrieve(mp4_url, output_path, reporthook=dl_progress)
    except:
        print(f"An exception occurred while downloading clip {clip['id']}")


def add_text_to_video(input_file, output_file, text, font_file):
    command = [
        'ffmpeg', '-i', input_file, '-vf',
        f"fps=60,drawtext=fontfile={font_file}:text='{text}':x=w-tw-10:y=h-th-10:fontsize=72:fontcolor=white:box=1:boxcolor=black@0.5",
        '-c:v', 'h264_nvenc', '-preset', 'fast', '-cq', '23', '-qmin', '20', '-qmax', '25', '-codec:a', 'copy', output_file
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error adding text to video: {e}")
        sys.exit(1)

def concatenate_videos(input_files, output_file, image_video_file=None):
    video_scale_filter = "".join([f"[{i}:v:0]scale=1920:1080,setsar=1[{i}v];" for i in range(len(input_files))])
    video_concat_filter = "".join([f"[{i}v]" for i in range(len(input_files))])
    audio_concat_filter = "".join(["[{}:a:0]".format(i) for i in range(len(input_files))])
    concat_filter = f"{video_scale_filter}{video_concat_filter}concat=n={len(input_files)}:v=1:a=0[outv];{audio_concat_filter}concat=n={len(input_files)}:v=0:a=1[outa]"
    
    if image_video_file:
        input_files = input_files.copy()  # Create a copy of the input_files list to avoid modifying the original list
        input_files.append(image_video_file)

    command = ['ffmpeg']
    for i, input_file in enumerate(input_files):
        command.extend(['-i', input_file])
    command.extend(['-filter_complex', concat_filter, '-map', '[outv]', '-map', '[outa]', '-c:v', 'h264_nvenc', '-preset', 'fast', '-r', '60', '-cq', '23', '-qmin', '20', '-qmax', '25', '-c:a', 'aac', '-b:a', '128k', output_file])
    
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error concatenating videos: {e}")
        sys.exit(1)



def create_video_from_image(image_file, output_file, duration):
    command = [
        'ffmpeg', '-loop', '1', '-i', image_file, '-c:v', 'h264_nvenc', '-t', str(duration), '-pix_fmt', 'yuv420p', output_file
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error creating video from image: {e}")
        sys.exit(1)
