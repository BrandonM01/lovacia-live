import os
from moviepy.editor import VideoFileClip

def process_video(path, trim_start, trim_end, flip, suffix=""):
    clip = VideoFileClip(path)
    if trim_end: clip = clip.subclip(trim_start, trim_end)
    if flip:    clip = clip.fx(vfx.mirror_x)
    out_name = os.path.splitext(os.path.basename(path))[0] + suffix + ".mp4"
    out_path = os.path.join("uploads", out_name)
    clip.write_videofile(out_path, codec="libx264")
    return out_name
