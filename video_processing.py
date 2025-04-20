import os, random
from moviepy.editor import VideoFileClip, vfx

def process_video_variants(path, base, ext, count, flip, trim_start, trim_end):
    out = []
    clip0 = VideoFileClip(path)
    # apply trim once
    if trim_end > 0:
        clip0 = clip0.subclip(trim_start, trim_end)
    for i in range(1, count+1):
        clip = clip0
        if flip:
            clip = clip.fx(vfx.mirror_x)
        fname = f"{base}_vid{i}{ext}"
        clip.write_videofile(os.path.join("uploads", fname), audio_codec="aac", verbose=False, logger=None)
        out.append(fname)
    clip0.close()
    return out
