import streamlit as st
import random
import tempfile
import base64
from gtts import gTTS
from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip, ColorClip

# -------------------------------
# Sample sentences
sample_sentences = {
    "PRE-KG": ["A B C D.", "Red, blue, green.", "One, two, three, four."],
    "UKG": ["Elephant has a trunk.", "Fish swims in water.", "Goat eats grass.", "House is big."],
    "PhD": ["Computational fluid dynamics governs complex flow behavior in turbulent regimes."]
}

# -------------------------------
# Generate text
def generate_text(level, minutes):
    total_words = minutes * 20
    sentences = sample_sentences.get(level, [])
    paragraph = ""
    last = ""
    while len(paragraph.split()) < total_words:
        choice = random.choice(sentences)
        if choice != last:
            paragraph += " " + choice
            last = choice
    return paragraph.strip()

# -------------------------------
# Convert text to speech
def text_to_speech(text):
    tts = gTTS(text)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

# -------------------------------
# Generate video
def generate_video(text, audio_path, duration=10):
    # Background color video
    bg = ColorClip(size=(1280, 720), color=(30, 30, 30), duration=duration)

    # Add text on video
    txt_clip = TextClip(text, fontsize=40, color='white', size=(1000, None), method='caption', align='center')
    txt_clip = txt_clip.set_position('center').set_duration(duration)

    # Add audio
    audio = AudioFileClip(audio_path)
    bg = bg.set_audio(audio)

    # Merge
    video = CompositeVideoClip([bg, txt_clip])
    
    # Save final video
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    video.write_videofile(output_path, fps=24)
    return output_path

# -------------------------------
# UI
st.set_page_config(page_title="🎥 AI Video Generator", layout="centered")
st.title("🎬 AI Video Generator: PRE-KG to PhD")

level = st.selectbox("Select your level:", list(sample_sentences.keys()))
minutes = st.slider("Video length (minutes):", 1, 3, 1)

target_text = generate_text(level, minutes)
st.subheader("Generated Text:")
st.markdown(f"<div style='background:#f0f8ff;padding:15px'>{target_text}</div>", unsafe_allow_html=True)

if st.button("🎥 Generate Video"):
    with st.spinner("Generating speech..."):
        audio_file = text_to_speech(target_text)

    with st.spinner("Generating video..."):
        video_file = generate_video(target_text, audio_file, duration=minutes*10)  # 10 sec per minute
    
    st.success("✅ Video generated successfully!")

    # Show video
    video_bytes = open(video_file, "rb").read()
    st.video(video_bytes)

    # Download option
    b64 = base64.b64encode(video_bytes).decode()
    href = f'<a href="data:video/mp4;base64,{b64}" download="output.mp4">📥 Download Video</a>'
    st.markdown(href, unsafe_allow_html=True)
