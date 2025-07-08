import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  

model = genai.GenerativeModel('gemini-pro')

def get_movie_description(title):
    try:
        response = model.generate_content(f"Give a 1-2 sentence brief and friendly movie description for '{title}'")
        return response.text
    except Exception:
        return "Açıklama getirilemedi."
