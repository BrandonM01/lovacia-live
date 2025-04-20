from moviepy.editor import VideoFileClip
import os

def process_video(input_path: str, trim_start: float, trim_end: float, flip: bool) -> str:
    clip = VideoFileClip(input_path)
    # optional trim
    if trim_end > 0:
        clip = clip.subclip(trim_start, trim_end)
    # optional flip
    if flip:
        clip = clip.fx(vfx.mirror_x)
    # write out
    base, ext = os.path.splitext(input_path)
    out_path = f"{base}_proc.mp4"
    clip.write_videofile(out_path, codec="libx264", audio_codec="aac")
    clip.close()
    return out_path
