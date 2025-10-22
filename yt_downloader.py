import os
import subprocess
from pytubefix import YouTube

def download_video_adaptive(link, quality="720p", start_time=None, end_time=None):
    yt = YouTube(link)
    print(f"Downloading from: {yt.title}")

    # Filter for video-only streams with requested resolution
    video_stream = yt.streams.filter(adaptive=True, only_video=True, res=quality).first()
    if not video_stream:
        print(f"No video stream found for {quality}, falling back to highest video quality available")
        video_stream = yt.streams.filter(adaptive=True, only_video=True).order_by("resolution").desc().first()

    # Filter for audio-only streams
    audio_stream = yt.streams.filter(adaptive=True, only_audio=True, mime_type="audio/mp4").order_by("abr").desc().first()
    if not audio_stream:
        print("No audio stream found, downloading audio separately may fail.")
    
    print(f"Downloading video stream: {video_stream.resolution} {video_stream.mime_type}")
    video_file = video_stream.download(filename="video_temp.mp4")

    print(f"Downloading audio stream: {audio_stream.abr} {audio_stream.mime_type}")
    audio_file = audio_stream.download(filename="audio_temp.mp4")

    # Prepare output file name
    base_name = yt.title.replace(" ", "_").replace("|", "").replace("/", "")  # simple safe name
    output_file = f"{base_name}_merged.mp4"

    # Create ffmpeg merge command
    # Optionally, trim if start and end time specified
    if start_time is not None:
        start_time_sec = start_time
    else:
        start_time_sec = 0

    # If end_time is None, do not provide duration to ffmpeg (merge full)
    if end_time is not None and end_time > start_time_sec:
        duration = end_time - start_time_sec
        trim_cmd = ["-ss", str(start_time_sec), "-t", str(duration)]
    elif start_time_sec > 0:
        trim_cmd = ["-ss", str(start_time_sec)]
    else:
        trim_cmd = []

    cmd = [
        "ffmpeg",
        "-y",
        *trim_cmd,
        "-i", video_file,
        "-i", audio_file,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        output_file
    ]

    print("Merging video and audio with ffmpeg...")
    subprocess.run(cmd, check=True)
    print(f"Saved merged output as: {output_file}")

    # Remove temp files
    os.remove(video_file)
    os.remove(audio_file)

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=JP7WM82XO4g&pp=ygUOY2xvdWQgd2l0aCByYWo%3D"
    download_video_adaptive(video_url, quality=None, start_time=00, end_time=None)
