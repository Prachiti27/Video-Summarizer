import whisper
import yt_dlp
import os
import uuid

ffmpeg_path = r"C:\Users\Prachi\ffmpeg\bin"
if ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + ffmpeg_path

class SpeechToText:
    @staticmethod
    def transcribe_from_youtube(url):
        random_id = str(uuid.uuid4())
        audio_file_no_ext = f"temp_{random_id}"
        expected_final_file = f"{audio_file_no_ext}.mp3"

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": audio_file_no_ext, 
            "quiet": False, 
            "javascript_runtimes": ["node"], 
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            raise RuntimeError(f"YouTube download failed: {e}")
            
        if not os.path.exists(expected_final_file):
            raise FileNotFoundError(f"Audio file not found: {expected_final_file}. Ensure Node.js and FFmpeg are correctly installed.")

        model = whisper.load_model("base")
        result = model.transcribe(expected_final_file)

        if os.path.exists(expected_final_file):
            os.remove(expected_final_file)

        return result["text"]