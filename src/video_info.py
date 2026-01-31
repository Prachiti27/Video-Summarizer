from os import link
from turtle import title
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
import requests
import re
from src.stt import SpeechToText

class GetVideo:
    @staticmethod
    def Id(link):
        if "youtube.com" in link:
            pattern = r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)'
            video_id = re.search(pattern, link).group(1)
            return video_id
        elif "youtu.be" in link:
            pattern = r'youtu\.be/([a-zA-Z0-9+-]+)'
            video_id = re.search(pattern, link).group(1)
            return video_id
        else:
            return None
        
    @staticmethod
    def title(link):
        r = requests.get(link)
        s = BeautifulSoup(r.text, "html.parser")

        try:
            return s.find("meta", itemprop="name")["content"]
        except Exception:
            return "Unable to fetch video title"
        
    @staticmethod
    def transcript(link):
        video_id = GetVideo.Id(link)
        if not video_id:
            return None

        try:
            data = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
            return " ".join(i["text"] for i in data)

        except Exception as e:
            print(f"Official transcript failed, switching to Whisper: {e}")
            try:
                return SpeechToText.transcribe_from_youtube(link)
            except Exception as whisper_err:
                print(f"Whisper transcription failed: {whisper_err}")
                return None 

    @staticmethod
    def transcript_time(link):
        video_id = GetVideo.Id(link)
        if not video_id:
            return ""

        try:
            data = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
            final = ""
            for i in data:
                t = int(round(i["start"]))
                h = t // 3600
                m = (t % 3600) // 60
                s = t % 60
                final += f'{i["text"]} (time:{h:02d}:{m:02d}:{s:02d}) '
            return final

        except Exception as e:
            print("Timestamp transcript error:", e)
            return ""
