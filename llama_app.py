import streamlit as st
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi

# ------------------------------------------------------------
# Function: Fetch YouTube transcript
# ------------------------------------------------------------
def fetch_youtube_transcript(video_id: str, languages: list = None) -> str:
    if languages is None:
        languages = ["en"]
    fetched_transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
    transcript_text = " ".join([segment["text"] for segment in fetched_transcript])
    return transcript_text

# ------------------------------------------------------------
# Function: Run LLaMA 3 via Ollama
# ------------------------------------------------------------
def run_llama3_locally(prompt: str, model_name="llama3.1:8b") -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", model_name],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180
        )
        if result.returncode != 0:
            raise Exception(f"Ollama error: {result.stderr.decode()}")
        return result.stdout.decode()
    except Exception as e:
        return f"❌ Error running local LLaMA model: {e}"

# ------------------------------------------------------------
# Streamlit App
# ------------------------------------------------------------
st.set_page_config(page_title="Social Media Generator", page_icon="📱", layout="wide")
st.title("📱 Social Media Content Generator with LLaMA 3.1")

video_id = st.text_input("YouTube Video ID", placeholder="e.g., OZ5OZZZ2cvk")
query = st.text_area("Your Query", placeholder="e.g., Generate a LinkedIn post and an Instagram caption based on this video")

st.subheader("Select Platforms")
linkedin = st.checkbox("LinkedIn", value=True)
instagram = st.checkbox("Instagram", value=True)
twitter = st.checkbox("Twitter")

if st.button("Generate Content", type="primary"):
    if not video_id:
        st.error("Please enter a YouTube Video ID")
    else:
        selected_platforms = []
        if linkedin:
            selected_platforms.append("LinkedIn")
        if instagram:
            selected_platforms.append("Instagram")
        if twitter:
            selected_platforms.append("Twitter")

        if not selected_platforms:
            st.error("Please select at least one platform")
        else:
            try:
                with st.spinner("Fetching transcript and generating content..."):
                    transcript = fetch_youtube_transcript(video_id)
                    truncated = transcript[:10000]  # Optional: truncate for token limit

                    platform_str = " and ".join(selected_platforms)
                    final_prompt = (
                        f"You are a social media content creator. Generate engaging, creative posts for {platform_str}.\n\n"
                        f"{query.strip()}\n\n"
                        f"Transcript:\n{truncated}"
                    )
                    output = run_llama3_locally(final_prompt)

                st.header("Generated Content")
                for platform in selected_platforms:
                    with st.expander(f"{platform} Post", expanded=True):
                        st.text_area(f"{platform} Content", output, height=200)
                        st.download_button(
                            label=f"Download {platform} Content",
                            data=output,
                            file_name=f"{platform.lower()}_post.txt",
                            mime="text/plain"
                        )

            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("💡 Powered by local LLaMA 3.1 via Ollama and YouTube Transcript API")
