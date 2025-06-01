import asyncio
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    CouldNotRetrieveTranscript, 
    VideoUnavailable,
    InvalidVideoId, 
    NoTranscriptFound,
    TranscriptsDisabled
)

# ------------------------------------------------------------
# Function: Fetch YouTube transcript
# ------------------------------------------------------------
def fetch_youtube_transcript(video_id: str, languages: list = None) -> str:
    if languages is None:
        languages = ["en"]

    try:
        fetched_transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        transcript_text = " ".join([segment["text"] for segment in fetched_transcript])
        return transcript_text
    except Exception as e:
        if isinstance(e, NoTranscriptFound):
            error_msg = f"No transcript found for video {video_id} in languages: {languages}"
        elif isinstance(e, VideoUnavailable):
            error_msg = f"Video {video_id} is unavailable"
        elif isinstance(e, InvalidVideoId):
            error_msg = f"Invalid video ID: {video_id}"
        elif isinstance(e, TranscriptsDisabled):
            error_msg = f"Transcripts are disabled for video {video_id}"
        elif isinstance(e, CouldNotRetrieveTranscript):
            error_msg = f"Could not retrieve transcript: {str(e)}"
        else:
            error_msg = f"An unexpected error occurred: {str(e)}"
        raise Exception(error_msg) from e

# ------------------------------------------------------------
# Function: Run LLaMA 3 via Ollama
# ------------------------------------------------------------
def run_llama3_locally(prompt: str, model_name="llama3.1:8b") -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", model_name],
            input=prompt.encode(),
            stdout=subprocess.PIPE, # Captures the standard output (the model’s response).
            stderr=subprocess.PIPE,
            timeout=180  # Adjust if needed
        )
        if result.returncode != 0:
            raise Exception(f"Ollama error: {result.stderr.decode()}")
        return result.stdout.decode()
    except Exception as e:
        print(f"Error running local LLaMA model: {e}")
        return "Error generating content."

# ------------------------------------------------------------
# Function: Generate social media post from transcript
# ------------------------------------------------------------
def generate_social_media_post(transcript: str, platform: str) -> str:
    prompt = (
        f"You are a social media content creator. based on given social media Generate an engaging and atractive or professional for {platform} and if nesesary, use Emojies\n\n"
        f"based on the following YouTube transcript:\n\n{transcript}"
    )
    print(f"\n🧠 Generating post for {platform}...\n")
    return run_llama3_locally(prompt)

# ------------------------------------------------------------
# Main async function
# ------------------------------------------------------------
async def main():
    video_id = "qU3fmidNbJE"  # Replace with your video ID
    try:
        transcript = fetch_youtube_transcript(video_id)
        # Truncate if transcript is too long (keep under 4000 tokens for LLaMA)
        truncated_transcript = transcript[:10000] if len(transcript) > 10000 else transcript
        result = generate_social_media_post(truncated_transcript, "Instagram")
        
        try:
            with open('Generated_Blog_Post_1.md','w') as file:
                file.write(result)
        except Exception as e:
            print(f"Error saving post to file: {e}")
        # Print the generated post
        
        print("📢 Generated Post:\n")
        print(result)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
