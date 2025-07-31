# RAG Course Chatbot

## Features
- Retrieval-Augmented Generation (RAG) chatbot for course info
- Two modes: SQLDatabaseChain (strict SQL) and VectorStore (semantic search)
- Multilingual (IT/EN), no hallucination, 100% data-backed
- Streamlit UI included

## Setup
1. `pip install -r requirements.txt`
2. Set `OPENAI_API_KEY` as env variable
3. Run: `python rag_chatbot.py` or `streamlit run streamlit_app.py`

## Extending
- Add columns/tables in `db_utils.py` and `prompts.py`
- Adjust vector store in `vector_utils.py`

## Testing
- `pytest test_rag_chatbot.py`

## Example Interactions
- Input: "Quali sono i requisiti del corso FER?"
- Output: [Lists requirements in Italian]
- Input: "Which courses are under 200 euros?"
- Output: [Lists matching courses in English with prices]
- Input: "Parlami del corso ECO-BONUS"
- Output: [Full course details in Italian] 

import streamlit.components.v1 as components

def browser_tts(text, lang="en"):
    js = f"""
    <script>
    var msg = new SpeechSynthesisUtterance({text!r});
    msg.lang = {lang!r};
    window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js)

---

## 1. **Use Browser-Native Text-to-Speech (Recommended for Streamlit)**

Modern browsers have built-in, instant, and much more natural TTS voices via the [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis). You can trigger this from Streamlit using a custom component or a little JavaScript.

### **How to Add Browser TTS in Streamlit**

Add this function to your `streamlit_app.py`:
```python
import streamlit.components.v1 as components

def browser_tts(text, lang="en"):
    js = f"""
    <script>
    var msg = new SpeechSynthesisUtterance({text!r});
    msg.lang = {lang!r};
    window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js)
```

**Usage:**  
After displaying the assistant's response, add:
```python
if st.button("🔊 Speak", key=f"tts_{i}"):
    browser_tts(msg["content"], lang=st.session_state.last_lang)
```
- This will use the browser’s best available voice, which is much more natural and instant.

---

## 2. **Remove gTTS for UI Speech**

- You can keep gTTS for CLI or fallback, but for the web UI, browser TTS is faster and more natural.

---

## 3. **Optional: Use a Premium TTS API**

If you want even more natural voices, you can use APIs like:
- [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech)
- [Microsoft Azure TTS](https://azure.microsoft.com/en-us/products/ai-services/text-to-speech)
- [Amazon Polly](https://aws.amazon.com/polly/)
- [ElevenLabs](https://elevenlabs.io/) (very natural, but paid)

But for most use cases, browser TTS is fast, free, and good enough.

---

## 4. **Summary**

- **Browser TTS:** Fast, natural, no server-side audio generation, works instantly.
- **gTTS:** Robotic, slow, but works everywhere (including CLI).

---

## Would you like me to update your Streamlit app to use browser-native TTS for instant, natural speech?  
This will make your bot sound much more human and respond instantly when you click "🔊 Speak"! 