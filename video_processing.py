import moviepy.editor as mp

def process_video(input_video_path, trim_start=5, trim_end=10, flip=False):
    # Load the video
    video = mp.VideoFileClip(input_video_path)
    
    # Trim the video
    video = video.subclip(trim_start, trim_end)
    
    # Optionally flip the video
    if flip:
        video = video.fx(mp.vfx.mirror_x)
    
    # Save the processed video
    output_video_path = "processed_" + input_video_path
    video.write_videofile(output_video_path, codec="libx264")

    return output_video_path  # Return the processed video path
