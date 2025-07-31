from langdetect import detect

def detect_language(text):
    try:
        lang = detect(text)
        return "it" if lang == "it" else "en"
    except Exception:
        return "en" 