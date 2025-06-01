# checking the function

from social_media_agent import fetch_youtube_transcript

def main():
    # Example YouTube video ID
    video_id = "qU3fmidNbJE"  # Replace with a valid YouTube video ID
    # 2MyUD8E1GLI
    # qEpmS_9tA9A
    # OZ5OZZZ2cvk
    # qU3fmidNbJE
    try:
        # Fetch the transcript for the given video ID
        transcript = fetch_youtube_transcript(video_id)
        print("Transcript fetched successfully:")
        print(transcript)
    except Exception as e:
        print(f"An error occurred while fetching the transcript: {e}")
if __name__ == "__main__":
    main()