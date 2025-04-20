from moviepy.editor import VideoFileClip, vfx

def process_video(
    path: str,
    trim_start: float = 0,
    trim_end: float = None,
    flip: bool = False
) -> str:
    clip = VideoFileClip(path)

    # optional trim
    if trim_end is not None:
        clip = clip.subclip(trim_start, trim_end)

    # optional flip
    if flip:
        clip = clip.fx(vfx.mirror_x)

    # write file
    output = "processed_video.mp4"
    clip.write_videofile(output, codec="libx264", audio_codec="aac")
    return output
