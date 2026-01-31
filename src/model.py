import os
from dotenv import load_dotenv
from google import genai as genai
from openai import OpenAI

class Model:
    def __init__(self):
        load_dotenv()
        
    @staticmethod
    def google_gemini(transcript, prompt, extra="", model_type="gemini-1.5-flash"):
        load_dotenv()

        if transcript is None:
            return "Error: Transcript is empty or unavailable."

        try:
            client = genai.Client(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
            full_prompt = f"{prompt}{extra}{transcript}"
            response = client.models.generate_content(
                model=model_type,
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            return f"Gemini error: {str(e)}"
        
    @staticmethod
    def openai_chatgpt(transcript, prompt, extra=""):
        load_dotenv()
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = "gpt-3.5-turbo"
        message = [{"role": "system", "content": prompt + extra + transcript}]
        try:
            response = client.chat.completions.create(model=model, messages=message)
            return response.choices[0].message.content
        except Exception as e:
            response_error = "There is an error with API key or eith python module."
            return response_error, str(e)