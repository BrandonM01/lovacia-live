from moviepy.editor import VideoFileClip, vfx  # note import vfx for flipping

def process_video(
    input_path: str,
    trim_start: float = 0,
    trim_end: float = None,
    flip: bool = False,
) -> str:
    clip = VideoFileClip(input_path)
    if trim_end is not None:
        clip = clip.subclip(trim_start, trim_end)
    if flip:
        clip = clip.fx(vfx.mirror_x)  # mirror horizontally
    output_path = "processed_video.mp4"
    clip.write_videofile(output_path, audio_codec="aac")
    clip.close()
    return output_path
