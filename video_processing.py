import subprocess, os

def process_video(input_path: str, trim_start: float, trim_end: float, flip: bool) -> str:
    base, _ = os.path.splitext(input_path)
    out_path = f"{base}_proc.mp4"

    # build ffmpeg command
    cmd = ["ffmpeg", "-y"]

    # input + trim
    if trim_end > 0:
        cmd += ["-ss", str(trim_start), "-to", str(trim_end), "-i", input_path]
    else:
        cmd += ["-i", input_path]

    # filters
    filters = []
    if flip:
        filters.append("hflip")

    if filters:
        cmd += ["-vf", ",".join(filters)]

    cmd += ["-c:v", "libx264", "-c:a", "aac", out_path]

    subprocess.run(cmd, check=True)
    return out_path
