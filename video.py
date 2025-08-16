import os
import subprocess
import yt_dlp as ydl

# Define video URLs and corresponding mood names
video_info = [
    ("https://www.youtube.com/watch?v=QFOJhn7khhE", "dungeon_caves"),
    ("https://www.youtube.com/watch?v=mnB2yet7dtk", "magic_supernatural"),
    ("https://www.youtube.com/watch?v=Zb8PxCCFrRE", "exploration_travel"),
    ("https://www.youtube.com/watch?v=azfOryn3600", "combat_danger"),
    ("https://www.youtube.com/watch?v=Ag8sbpNXBEQ", "town_social"),
    ("https://www.youtube.com/watch?v=5Jzp5H4mQVE", "mystery_investigation"),
    ("https://www.youtube.com/watch?v=vMBKEZvZ7qU", "relax_safe_inn")
]

# Download and convert each video
for url, mood in video_info:
    # Download audio using yt-dlp
    with ydl.YoutubeDL({'format': 'bestaudio/best', 'outtmpl': './audio/%(id)s.%(ext)s'}) as ydl_opts:
        info_dict = ydl_opts.extract_info(url, download=True)
        file_path = f"./audio/{info_dict['id']}.{info_dict['ext']}"

    # Convert to .ogg using ffmpeg
    output_path = f"./audio/{mood}.ogg"
    subprocess.run(['ffmpeg', '-i', file_path, '-vn', '-acodec', 'libvorbis', output_path])

    # Remove the original file after conversion
    os.remove(file_path)

print("Download and conversion complete.")
