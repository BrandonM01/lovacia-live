import os
import subprocess
from typing import List

def process_video_variants(input_path: str) -> List[str]:
    """
    Given an input video file, produces two variants:
      1) horizontally flipped
      2) slowed down (50% speed)
    Returns a list of output file paths.
    """
    out_files = []
    base, ext = os.path.splitext(input_path)

    # 1) horizontal flip
    hflip = f"{base}_hflip{ext}"
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-vf", "hflip",
        hflip
    ], check=True)
    out_files.append(hflip)

    # 2) half‑speed (slow down)
    slow = f"{base}_half_speed{ext}"
    # for video: setpts=2*PTS, for audio: atempo=0.5
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-filter_complex",
        "[0:v]setpts=2.0*PTS[v];[0:a]atempo=0.5[a]",
        "-map", "[v]", "-map", "[a]",
        slow
    ], check=True)
    out_files.append(slow)

    return out_files
