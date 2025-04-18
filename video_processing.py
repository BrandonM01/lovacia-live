from moviepy.editor import VideoFileClip
from moviepy import editor as mp
from moviepy.editor import vfx

def process_video(video_path, trim_start=0, trim_end=10, flip=False):
    # Load the video clip
    clip = VideoFileClip(video_path)
    
    # Trim video if needed
    clip = clip.subclip(trim_start, trim_end)

    # Flip video horizontally if needed
    if flip:
        clip = clip.fx(vfx.mirror_x)

    # Save the processed video
    output_path = 'processed_video.mp4'
    clip.write_videofile(output_path)
    return output_path

