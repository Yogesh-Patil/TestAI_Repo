import os
from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, vfx
from PIL import ImageFont

# --- Configuration ---
QUOTE = "The best way to get started is to quit talking and begin doing."
AUTHOR = "– Walt Disney"
BACKGROUND_IMAGE = "background.jpg"  # replace with your actual path
BACKGROUND_MUSIC = "background.mp3"  # optional
OUTPUT_FILE = "quote_video.mp4"

# --- Create background image clip ---
image_clip = ImageClip(BACKGROUND_IMAGE, duration=10)


# Verify Pillow can load font
font_path = r"C:\Windows\Fonts\arialbd.ttf"
ImageFont.truetype(font_path, 50)  # sanity check

text_clip = TextClip(
    text=f'"{QUOTE}"\n{AUTHOR}',
    color="white",
    font=font_path,   # ✅ absolute path to .ttf file
    font_size=50,
    size=image_clip.size,
    method="caption",
).with_duration(image_clip.duration)

# --- Apply fade effects using vfx ---
image_clip = image_clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])
text_clip = text_clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])

# --- Combine clips ---
final = CompositeVideoClip([image_clip, text_clip.with_position("center")])

# --- Optional background music ---
if os.path.exists(BACKGROUND_MUSIC):
    audio_clip = AudioFileClip(BACKGROUND_MUSIC).with_duration(final.duration)
    final = final.with_audio(audio_clip)

# --- Export final video ---
final.write_videofile(
    OUTPUT_FILE,
    fps=24,
    codec="libx264",
    audio_codec="aac",
    preset="medium"
)
