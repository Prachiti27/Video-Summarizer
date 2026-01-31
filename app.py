import streamlit as st
import os
from dotenv import load_dotenv

from src.video_info import GetVideo
from src.model import Model
from src.prompt import Prompt
from src.misc import Misc
from src.timestamp_formatter import TimestampFormatter
from src.copy_module_edit import ModuleEditor
from st_copy_to_clipboard import st_copy_to_clipboard


class AIVideoSummarizer:
    def __init__(self):
        load_dotenv()

        self.youtube_url = ""
        self.video_id = None
        self.video_title = None

        self.model_name = None
        self.gemini_model_type = "gemini-1.5-flash"

        self.col1 = self.col2 = self.col3 = None

    def setup_page(self):
        st.set_page_config(
            page_title="AI Video Summarizer",
            page_icon="📊",
            layout="wide"
        )
        st.title("AI Video Summarizer")

        editor = ModuleEditor("st_copy_to_clipboard")
        editor.modify_frontend_files()

        self.col1, self.col2, self.col3 = st.columns(3)

    def get_youtube_info(self):
        with self.col1:
            self.youtube_url = st.text_input("Enter YouTube Video Link")

            if not self.youtube_url:
                return

            self.video_id = GetVideo.Id(self.youtube_url)
            if not self.video_id:
                st.error("Invalid YouTube link.")
                st.stop()

            self.video_title = GetVideo.title(self.youtube_url)
            st.markdown(f"**{self.video_title}**")

            st.image(
                f"https://img.youtube.com/vi/{self.video_id}/0.jpg",
                width=320
            )

    def select_model(self):
        available_models = []

        if os.getenv("GOOGLE_GEMINI_API_KEY"):
            available_models.append("Gemini")
        if os.getenv("OPENAI_API_KEY"):
            available_models.append("ChatGPT")

        if not available_models:
            st.warning("No API keys found in environment.")
            st.stop()

        with self.col2:
            self.model_name = st.selectbox(
                "Select the model",
                available_models
            )

            if self.model_name == "Gemini":
                st.image(
                    "https://i.imgur.com/w9izNH5.png",
                    width=120
                )
                self.gemini_model_type = st.selectbox(
                    "Select Gemini Model",
                    ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"],
                    index=0
                )
            else:
                st.image(
                    "https://i.imgur.com/Sr9e9ZC.png",
                    width=120
                )

    def generate_summary(self):
        transcript = GetVideo.transcript(self.youtube_url)

        if transcript is None:
            st.error(
                "Transcript could not be retrieved via YouTube API.\n\n"
                "This video may block transcript access."
            )
            return

        if self.model_name == "Gemini":
            result = Model.google_gemini(
                transcript=transcript,
                prompt=Prompt.prompt1(),
                model_type=self.gemini_model_type
            )
        else:
            result = Model.openai_chatgpt(
                transcript=transcript,
                prompt=Prompt.prompt1()
            )

        st.markdown("## Summary")
        st.write(result)
        st_copy_to_clipboard(str(result))

    def generate_timestamps(self):
        transcript_time = GetVideo.transcript_time(self.youtube_url)

        if not transcript_time:
            st.error("Transcript with timestamps is unavailable.")
            return

        video_link = f"https://youtube.com/watch?v={self.video_id}"

        if self.model_name == "Gemini":
            result = Model.google_gemini(
                transcript=transcript_time,
                prompt=Prompt.prompt1(ID="timestamp"),
                extra=video_link,
                model_type=self.gemini_model_type
            )
        else:
            result = Model.openai_chatgpt(
                transcript=transcript_time,
                prompt=Prompt.prompt1(ID="timestamp"),
                extra=video_link
            )

        st.markdown("## Timestamps")
        st.markdown(result)

        formatted = TimestampFormatter.format(result)
        st_copy_to_clipboard(str(formatted))

    def generate_transcript(self):
        transcript = GetVideo.transcript(self.youtube_url)

        if not transcript:
            st.error("Transcript unavailable for this video.")
            return

        st.markdown("## Transcript")

        st.download_button(
            label="Download Transcript",
            data=transcript,
            file_name=f"Transcript - {self.video_title}.txt"
        )

        st.write(transcript)
        st_copy_to_clipboard(transcript)

    def run(self):
        self.setup_page()
        self.get_youtube_info()

        if not self.youtube_url or not self.video_id:
            return

        self.select_model()

        n, loader = Misc.loaderx()

        with self.col3:
            mode = st.radio(
                "What do you want to generate?",
                ["AI Summary", "AI Timestamps", "Transcript"],
                index=0
            )

            with st.spinner(loader[n]):
                if mode == "AI Summary" and st.button("Get Summary"):
                    self.generate_summary()

                elif mode == "AI Timestamps" and st.button("Get Timestamps"):
                    self.generate_timestamps()

                elif mode == "Transcript" and st.button("Get Transcript"):
                    self.generate_transcript()

        st.write(Misc.footer(), unsafe_allow_html=True)

if __name__ == "__main__":
    app = AIVideoSummarizer()
    app.run()
