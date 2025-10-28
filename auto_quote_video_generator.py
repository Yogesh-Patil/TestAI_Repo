import os
import random
import textwrap
from datetime import datetime
from moviepy import (
    ImageClip,
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    vfx,
    afx,
)
from PIL import ImageFont

# === CONFIGURATION ===
QUOTES = [
    ("The best way to get started is to quit talking and begin doing.", "– Walt Disney"),
    ("Don’t let yesterday take up too much of today.", "– Will Rogers"),
    ("It’s not whether you get knocked down, it’s whether you get up.", "– Vince Lombardi"),
    ("If you are working on something exciting, it will keep you motivated.", "– Steve Jobs"),
    ("The future belongs to those who believe in the beauty of their dreams.", "– Eleanor Roosevelt"),
]

BACKGROUND_DIR = "backgrounds"   # folder with background videos or images
MUSIC_DIR = "music"              # folder with mp3/wav
OUTPUT_DIR = "generated_videos"

DURATION = 15                    # seconds per video
FONT_PATH = r"C:\Windows\Fonts\arialbd.ttf"
FONT_SIZE = 36
TEXT_COLOR = "white"
VIDEO_FPS = 24


# === UTILITIES ===

def pick_random_file(folder, extensions):
    """Pick a random file from a folder based on extension."""
    if not os.path.exists(folder):
        return None
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(extensions)]
    return random.choice(files) if files else None


def get_font_path():
    """Validate font file exists."""
    try:
        ImageFont.truetype(FONT_PATH, FONT_SIZE)
        return FONT_PATH
    except Exception as e:
        raise FileNotFoundError(f"Font not found or invalid: {FONT_PATH}\n{e}")


def pick_background_clip():
    """Pick a video clip if available, else fall back to an image."""
    video_file = pick_random_file(BACKGROUND_DIR, (".mp4", ".mov", ".avi", ".mkv"))
    if video_file:
        clip = VideoFileClip(video_file).without_audio().subclipped(0, DURATION)
    else:
        img_file = pick_random_file(BACKGROUND_DIR, (".jpg", ".png"))
        if not img_file:
            raise FileNotFoundError("No background found in 'backgrounds' folder.")
        clip = ImageClip(img_file, duration=DURATION)

    # Resize to portrait (1080x1920) for reels; adjust if needed
    return clip.resized(height=1920).resized(width=1080)


def create_wrapped_text_clip(quote, author, image_clip, FONT_SIZE, TEXT_COLOR, DURATION):
    """Create wrapped text clip centered on background."""
    wrap_width = max(20, int(image_clip.size[0] / (FONT_SIZE * 0.6)))
    wrapped_text = "\n".join(textwrap.wrap(quote, width=wrap_width))
    final_text = f'"{wrapped_text}"\n\n{author}'

    text_clip = (
        TextClip(
            text=final_text,
            color=TEXT_COLOR,
            font=get_font_path(),
            font_size=FONT_SIZE,
            method="caption",
            size=(int(image_clip.size[0] * 0.8), None),
            stroke_color="black",
            stroke_width=2,  # adds a slight shadow for readability
        )
        .with_duration(DURATION)
        .with_position(("center", "center"))
    )

    return text_clip


# === MAIN FUNCTION ===

def create_quote_video(quote, author):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    bg_clip = pick_background_clip()
    music_file = pick_random_file(MUSIC_DIR, (".mp3", ".wav"))

    print(f"🎨 Using background: {getattr(bg_clip, 'filename', 'image')}")
    print(f"🎵 Using music: {music_file or 'none'}")

    # Create text overlay
    text_clip = create_wrapped_text_clip(quote, author, bg_clip, FONT_SIZE, TEXT_COLOR, DURATION)

    # Fade-in/out effects — must be applied **before** composition
    bg_clip = bg_clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])
    text_clip = text_clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])

    # Merge layers
    final = CompositeVideoClip([bg_clip, text_clip])

    # Attach background audio
    if music_file and os.path.exists(music_file):
        try:
            audio_clip = AudioFileClip(music_file).with_effects([afx.AudioFadeOut(2)])
            audio_clip = audio_clip.subclipped(0, final.duration)
            final = final.with_audio(audio_clip)
        except Exception as e:
            print(f"⚠️ Failed to add audio: {e}")
            final = final.without_audio()
    else:
        final = final.without_audio()

    # Output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"quote_{timestamp}.mp4")

    print(f"💾 Exporting: {filename}")
    final.write_videofile(
        filename,
        fps=VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
    )

    print("✅ Video created successfully!\n")


# === RUN MULTIPLE QUOTES ===
if __name__ == "__main__":
    num_videos = 4  # change to number of videos to generate
    for i in range(num_videos):
        quote, author = random.choice(QUOTES)
        create_quote_video(quote, author)
