# -----------------------------------------------------------
# Step 0: Import necessary libraries
# -----------------------------------------------------------
import asyncio
import os
from youtube_transcript_api import YouTubeTranscriptApi
from agents import Agent, Runner, WebSearchTool, function_tool, ItemHelpers
from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List
# -----------------------------------------------------------
# Step 1: Get OpenAI API key
# -----------------------------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# -----------------------------------------------------------
# Step 2: Define Tools for the Agent
# -----------------------------------------------------------

# Tool: Generate Social Media from YouTube Transcript
@function_tool
def generate_content(video_transcript:str, social_media_platform:str):
    
    print(f"Generating content for {social_media_platform} from transcript...")
    # Initialize the OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    #Generate content using OpenAI
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "user",
                "content": f"You are a social media content creator. Generate a {social_media_platform} post based on the following YouTube transcript:\n\n{video_transcript}"
            }
        ],
        max_tokens=2500
    )
    content = response.output_text

    
# ------------------------------------------------------------
# Step 3: Define the Agent (content creator)
# ------------------------------------------------------------
@dataclass
class Post:
    platform: str
    content: str

content_writer_agent = Agent(
    name="ContentWriterAgent",
    instructions="""You are a social media content creator for social media platform.
                    Your task is to generate engaging posts for various social media platforms based on YouTube video transcripts.
                    You may use web search to find relevant information and generate content.""",
                    
    # instructions="""You are a talented content writer who writes engaging, humorous, informative and 
    #                 highly readable social media posts. 
    #                 You will be given a video transcript and social media platforms. 
    #                 You will generate a social media post based on the video transcript 
    #                 and the social media platforms.
    #                 You may search the web for up-to-date information on the topic and 
    #                 fill in some useful details if needed.""",
    model="gpt-3.5-turbo",
    
    tools=[
        WebSearchTool(),
        generate_content
    ],
    output_type=List[Post],
    
) 

# ------------------------------------------------------------
# Step 4: Define helper functions
# ------------------------------------------------------------
#fetch YouTube transcript from YouTube video ID
def fetch_youtube_transcript(video_id: str, languages: list = None) -> str:
    """
    Retrieves the transcript for a YouTube video.

    Args:
        video_id (str): The YouTube video ID.
        languages (list, optional): List of language codes to try, in order of preference.
                                   Defaults to ["en"] if None.

    Returns:
        str: The concatenated transcript text.

    Raises:
        Exception: If transcript retrieval fails, with details about the failure.
    """
    if languages is None:
        languages = ["en"]
    
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.get_transcript(video_id, languages=languages)
        
        #Concatenate all transcript segments into a single string
        transcript_text = " ".join([segment['text'] for segment in fetched_transcript])
        
        return transcript_text
    except Exception as e:
        # Handle specific YouTube transcript API exceptions
        from youtube_transcript_api._errors import (
            CouldNotRetrieveTranscript, 
            VideoUnavailable,
            InvalidVideoId, 
            NoTranscriptFound,
            TranscriptsDisabled
        )

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

        print(f"Error: {error_msg}")
        raise Exception(error_msg) from e
        
    # except Exception as e:
    #     from youtube_transcript_api import(
    #         NoTranscriptFound, 
    #         VideoUnavailable, 
    #         TranscriptsDisabled, 
    #         CouldNotRetrieveTranscript,
    #         InvalidVideoId
    #     )
        
    #     if isinstance(e, (NoTranscriptFound, VideoUnavailable, TranscriptsDisabled, CouldNotRetrieveTranscript, InvalidVideoId)):
            
    #         if isinstance(e, NoTranscriptFound):
    #             print("No transcript found for this video.")
    #         elif isinstance(e, VideoUnavailable):
    #             print("Video is unavailable.")
    #         elif isinstance(e, TranscriptsDisabled):
    #             print("Transcripts are disabled for this video.")
    #         elif isinstance(e, CouldNotRetrieveTranscript):
    #             print("Could not retrieve transcript for this video.")
    #         elif isinstance(e, InvalidVideoId):
    #             print("Invalid video ID provided.")
    #     else:
    #         print(f"An unexpected error occurred: {e}")
    #     return None

# ------------------------------------------------------------
# Step 5: Run the Agent
# ------------------------------------------------------------

async def main():
    video_id = "qEpmS_9tA9A"
    
    transcript = fetch_youtube_transcript(video_id)
    
    msg = f"Generate a post for Linkdin based on the following YouTube transcript:\n\n{transcript[:1000]}..."  # Truncate for brevity
    
    # Package input for the agent
    input_items = [{"content": msg, "role": "user"}]
    
    # Run content writer agent
    # Add trace to see the agent's execution steps
    # You can check the trace on https://platform.openai.com/traces
    
    result = await Runner.run(content_writer_agent, input_items)
    output = ItemHelpers.text_message_outputs(result.new_items)
    print(f"Generated content:\n",output)
    
if __name__ == "__main__":
    asyncio.run(main())
    
    