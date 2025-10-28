import os
import random
import textwrap
from datetime import datetime
from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, vfx
from PIL import ImageFont

# === CONFIGURATION ===
QUOTES = [
    ("The best way to get started is to quit talking and begin doing.", "– Walt Disney"),
    ("Don’t let yesterday take up too much of today.", "– Will Rogers"),
    ("It’s not whether you get knocked down, it’s whether you get up.", "– Vince Lombardi"),
    ("If you are working on something exciting, it will keep you motivated.", "– Steve Jobs"),
    ("The future belongs to those who believe in the beauty of their dreams.", "– Eleanor Roosevelt"),
]

BACKGROUND_DIR = "backgrounds"   # folder with background images
MUSIC_DIR = "music"              # folder with mp3 files (optional)
OUTPUT_DIR = "generated_videos"

DURATION = 15                    # seconds per video
FONT_PATH = r"C:\Windows\Fonts\arialbd.ttf"
FONT_SIZE = 32
TEXT_COLOR = "white"
VIDEO_FPS = 24


# === UTILITIES ===

def pick_random_file(folder, extensions):
    if not os.path.exists(folder):
        return None
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(extensions)]
    return random.choice(files) if files else None


def get_font_path():
    # Validate font file
    try:
        ImageFont.truetype(FONT_PATH, FONT_SIZE)
        return FONT_PATH
    except Exception as e:
        raise FileNotFoundError(f"Font not found or invalid: {FONT_PATH}\n{e}")

def create_wrapped_text_clip(quote, author, image_clip, FONT_SIZE, TEXT_COLOR, DURATION):
    # Adjust wrap width based on image width and font size
    wrap_width = max(20, int(image_clip.size[0] / (FONT_SIZE * 0.6)))  

    # Pre-wrap text manually to avoid broken words
    wrapped_text = "\n".join(textwrap.wrap(quote, width=wrap_width))
    final_text = f'"{wrapped_text}"\n\n– {author}'

    text_clip = TextClip(
            text=final_text,
            color=TEXT_COLOR,
            font=get_font_path(),
            font_size=FONT_SIZE,
            method="caption",  # still uses Pillow for nice rendering
            size=(int(image_clip.size[0] * 0.8), None),  # keep 80% width for margins
            stroke_color="black",
            stroke_width=2,
        ).with_duration(DURATION).with_position(("center", "center"))
    
    return text_clip

# === MAIN FUNCTION ===

def create_quote_video(quote, author):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    bg_image = pick_random_file(BACKGROUND_DIR, (".jpg", ".png")) or "background.jpg"
    music_file = pick_random_file(MUSIC_DIR, (".mp3", ".wav"))

    print(f"🎨 Using background: {bg_image}")
    print(f"🎵 Using music: {music_file or 'none'}")

    # Background image
    image_clip = ImageClip(bg_image, duration=DURATION)
    text_clip = create_wrapped_text_clip(quote, author, image_clip, FONT_SIZE, TEXT_COLOR, DURATION)
    
    # text_width = int(image_clip.size[0] * 0.8)  # wrap text to 80% of image width
    
    # text_clip = TextClip(
        # text=f'"{quote}"\n{author}',
        # color=TEXT_COLOR,
        # font=get_font_path(),
        # font_size=FONT_SIZE,
        # size=(text_width, None),    # auto height, limited width for wrapping
        # method="caption",           # Pillow-based text rendering
    # ).with_duration(DURATION).with_position(("center", "center"))

    # Fade effects
    image_clip = image_clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])
    text_clip = text_clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])

    # Merge
    final = CompositeVideoClip([image_clip, text_clip])

    # Optional music
    if music_file and os.path.exists(music_file):
        audio_clip = AudioFileClip(music_file).subclipped(0, DURATION)
        # audio_clip = audio_clip.audio_fadeout(2)
        final = final.with_audio(audio_clip)
    else:
        final = final.without_audio()
    
    final=final.resized((1080, 1920))
    
    # Output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"quote_{timestamp}.mp4")

    # Export
    print(f"💾 Exporting: {filename}")
    final.write_videofile(filename, fps=VIDEO_FPS, codec="libx264", audio_codec="aac", preset="medium")
    print("✅ Video created successfully!\n")


# === RUN MULTIPLE QUOTES ===
if __name__ == "__main__":
    num_videos = 2  # change to number of videos to generate
    for i in range(num_videos):
        quote, author = random.choice(QUOTES)
        create_quote_video(quote, author)
