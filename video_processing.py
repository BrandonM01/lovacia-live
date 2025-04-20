from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import mirror_x

def process_video(path: str, trim_start: float=0.0, trim_end: float | None=None, flip: bool=False) -> str:
    """
    - trim_start/end in seconds
    - flip: horizontal flip if True
    """
    clip = VideoFileClip(path)

    if trim_end is not None:
        clip = clip.subclip(trim_start, trim_end)

    if flip:
        clip = mirror_x(clip)

    out_path = "processed_video.mp4"
    # suppress verbose logging with logger=None
    clip.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
    clip.close()
    return out_path
