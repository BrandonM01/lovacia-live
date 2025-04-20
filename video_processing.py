import os
from moviepy.editor import VideoFileClip, vfx

def process_video_variants(video_path: str, output_dir: str) -> list[str]:
    """
    Load the clip and write out two variants:
      1) slowed down x0.5
      2) rotated 90°
    Returns the list of output file paths.
    """
    clip = VideoFileClip(video_path)
    name = os.path.splitext(os.path.basename(video_path))[0]

    variants: list[str] = []

    # slow motion
    slow = clip.fx(vfx.speedx, factor=0.5)
    slow_path = os.path.join(output_dir, f"{name}_slow.mp4")
    slow.write_videofile(slow_path, audio_codec="aac")
    variants.append(slow_path)

    # rotated
    rot = clip.fx(vfx.rotate, 90)
    rot_path = os.path.join(output_dir, f"{name}_rotated.mp4")
    rot.write_videofile(rot_path, audio_codec="aac")
    variants.append(rot_path)

    return variants
