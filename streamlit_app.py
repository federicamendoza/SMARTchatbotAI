import streamlit as st
import time
from language_utils import detect_language
import streamlit.components.v1 as components
from rag_chatbot import enhanced_chat
from langchain_ollama import ChatOllama
from prompts import format_course
import re
import streamlit.components.v1 as components
import json

def get_follow_up_decision(user_input, lang, llm, current_course):
    """
    Let the LLM decide if this is a follow-up question about the current course.
    No keyword matching - pure LLM intelligence.
    """
    course_title = current_course.get('titolo', 'No title')
    
    prompt = f"""
You are a smart assistant for Smart2t. Analyze if the user's question is a follow-up about the current course.

Current course: "{course_title}"
User question: "{user_input}"
Language: {lang}

IMPORTANT: Determine if the user is asking for more information about the CURRENT course, or if they are asking about something completely different (like company info, a different course, or general questions).

Examples of follow-up questions about the current course:
- "tell me more about this course"
- "what's the cost?"
- "how long is it?"
- "what are the requirements?"
- "describe this course"
- "explain this course"

Examples of NON-follow-up questions:
- "where is the company?"
- "what's the phone number?"
- "do you have other courses?"
- "show me Python courses"
- "hi"
- "thank you"

Respond with ONLY "yes" if it's a follow-up about the current course, or "no" if it's about something else:
"""
    
    try:
        result = llm.invoke(prompt)
        if hasattr(result, 'content'):
            decision = result.content.strip().lower()
        else:
            decision = str(result).strip().lower()
        
        # Clean up the response
        if "yes" in decision:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"[FOLLOW-UP DECISION ERROR] {e}")
        return False



def tts_controls(text, lang="en", key=None):
    """
    Crea controlli TTS che uniscono l'interfaccia avanzata (Play/Pausa/Riavvia)
    con la logica di selezione vocale di alta qualità.
    """
    text_json = json.dumps(text)
    lang_map = {"en": "en-US", "it": "it-IT"}
    browser_lang = lang_map.get(lang, "en-US")

    # Imposta il testo iniziale del bottone in base alla lingua
    speak_text = "▶️ Riproduci" if lang == "it" else "▶️ Speak"

    html_code = f"""
    <style>
        .tts-controls {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .tts-controls button {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background-color: #2b2d31; color: white; border: 1px solid #4f5257;
            border-radius: 8px; padding: 6px 12px;
            cursor: pointer; font-size: 16px; line-height: 1;
            transition: background-color 0.2s;
            width: 125px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        .tts-controls button:hover {{ background-color: #4f5257; }}
        .tts-controls button:disabled {{ cursor: not-allowed; opacity: 0.4; }}
        .tts-controls button#restart-btn-{key} {{ 
            width: auto;
            padding: 10px;
        }}
    </style>
    <div class="tts-controls" id="tts-controls-{key}">
        <button id="play-pause-btn-{key}" title="Play/Pause">{speak_text}</button>
        <button id="restart-btn-{key}" title="Restart" disabled>⏮️</button>
    </div>

    <script>
    (() => {{
        const playPauseBtn = document.getElementById('play-pause-btn-{key}');
        const restartBtn = document.getElementById('restart-btn-{key}');

        let utterance = null;
        const textToSpeak = {text_json};
        const langToSpeak = "{browser_lang}";
        
        const translations = {{
            it: {{ speak: '▶️ Riproduci', pause: '⏸️ Pausa', resume: '▶️ Riprendi' }},
            en: {{ speak: '▶️ Speak', pause: '⏸️ Pause', resume: '▶️ Resume' }}
        }};
        const currentLang = "{lang}";
        const T = translations[currentLang] || translations['en'];

        // --- INIZIO CODICE DEL TUO COLLEGA ---
        function getVoiceQualityScore(voice) {{
            let score = 0;
            const name = voice.name.toLowerCase();
            const lang = voice.lang.toLowerCase();
            if (name.includes('premium') || name.includes('enhanced') || name.includes('pro') || name.includes('natural') || name.includes('human') || name.includes('real')) score += 2000;
            if (name.includes('samantha') || name.includes('victoria') || name.includes('alex') || name.includes('daniel') || name.includes('karen') || name.includes('tom') || name.includes('fred') || name.includes('ralph') || name.includes('bruce') || name.includes('jill') || name.includes('vicki') || name.includes('lee') || name.includes('reed') || name.includes('susan') || name.includes('bells')) score += 1500;
            if (name.includes('david') || name.includes('zira') || name.includes('mark') || name.includes('eva') || name.includes('helena') || name.includes('jorge') || name.includes('pablo') || name.includes('miguel') || name.includes('elena') || name.includes('hazel') || name.includes('heera') || name.includes('kalpana') || name.includes('hemant') || name.includes('heera') || name.includes('kalia') || name.includes('neerja') || name.includes('priya') || name.includes('ravi') || name.includes('sabina') || name.includes('tracy') || name.includes('yating')) score += 1200;
            if (name.includes('google') || name.includes('microsoft') || name.includes('edge') || name.includes('chrome') || name.includes('chromium')) score += 1000;
            if (lang.startsWith('it')) {{
                if (name.includes('chiara') || name.includes('lucia') || name.includes('alice') || name.includes('federica') || name.includes('marco') || name.includes('paolo') || name.includes('roberto') || name.includes('silvia') || name.includes('elena') || name.includes('giulia')) score += 1800;
                score += 800;
            }}
            if (lang.startsWith('en')) score += 600;
            if (name.includes('female') || name.includes('woman') || name.includes('girl')) score += 400;
            if (!name.includes('remote') && !name.includes('network')) score += 200;
            if (name.includes('robot') || name.includes('mechanical') || name.includes('synthetic')) score -= 1000;
            return score;
        }}

        function findBestVoice(targetLang) {{
            const voices = window.speechSynthesis.getVoices();
            let bestVoice = null;
            let bestScore = -1;
            for (const voice of voices) {{
                if (voice.lang.startsWith(targetLang.substring(0, 2))) {{
                    const score = getVoiceQualityScore(voice);
                    if (score > bestScore) {{
                        bestScore = score;
                        bestVoice = voice;
                    }}
                }}
            }}
            console.log('Selected best voice:', bestVoice ? bestVoice.name : 'default');
            return bestVoice;
        }}
        // --- FINE CODICE DEL TUO COLLEGA ---

        function createAndPlayUtterance() {{
            window.speechSynthesis.cancel(); 
            utterance = new SpeechSynthesisUtterance(textToSpeak);
            utterance.lang = langToSpeak;
            
            // Applica la funzione per trovare la voce migliore
            utterance.voice = findBestVoice(langToSpeak);
            
            utterance.rate = 1.1;
            utterance.pitch = 1.1;

            utterance.onstart = () => {{ playPauseBtn.innerHTML = T.pause; restartBtn.disabled = false; }};
            utterance.onend = () => {{ playPauseBtn.innerHTML = T.speak; restartBtn.disabled = true; }};
            utterance.onpause = () => {{ playPauseBtn.innerHTML = T.resume; }};
            utterance.onresume = () => {{ playPauseBtn.innerHTML = T.pause; }};
            
            window.speechSynthesis.speak(utterance);
        }}

        playPauseBtn.addEventListener('click', () => {{
            if (window.speechSynthesis.paused) window.speechSynthesis.resume();
            else if (window.speechSynthesis.speaking) window.speechSynthesis.pause();
            else {{
                 if (window.speechSynthesis.getVoices().length === 0) {{
                    window.speechSynthesis.onvoiceschanged = createAndPlayUtterance;
                }} else {{
                    createAndPlayUtterance();
                }}
            }}
        }});

        restartBtn.addEventListener('click', () => {{
            window.speechSynthesis.cancel();
            setTimeout(() => window.speechSynthesis.speak(utterance), 100);
        }});
    }})();
    </script>
    """
    components.html(html_code, height=60)

st.set_page_config(page_title="Smart2t Course Chatbot", page_icon="🤖")
st.title("Smart2t Course Chatbot 🤖")

# Initialize session state
if "last_course_list" not in st.session_state:
    st.session_state.last_course_list = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_lang" not in st.session_state:
    st.session_state.last_lang = None  # Will be set by user selection
if "language_selected" not in st.session_state:
    st.session_state.language_selected = False  # Track if language has been selected
if "llm" not in st.session_state:
    st.session_state.llm = ChatOllama(model="llama3", base_url="http://localhost:11434")
if "course_list" not in st.session_state:
    st.session_state.course_list = []
if "waiting_for_selection" not in st.session_state:
    st.session_state.waiting_for_selection = False
if "current_course" not in st.session_state:
    st.session_state.current_course = None
if "waiting_for_follow_up" not in st.session_state:
    st.session_state.waiting_for_follow_up = False
if "follow_up_prompt" not in st.session_state:
    st.session_state.follow_up_prompt = None

# Voice selection sidebar
with st.sidebar:
    st.header("🎤 Ultra-High-Quality TTS Settings")
    
    # Professional mode indicator
    st.write("**🤖 Professional Mode:**")
    st.success("✅ RAG-First Approach: Always prioritizes database retrieval over LLM generation")
    st.info("🔍 Vector Search Only: Using semantic similarity for intelligent course matching")
    st.info("🎯 Data-Backed Responses: No hallucination, only factual information from courses database")
    
    # TTS info
    st.write("**🎯 Best Voice Selection:**")
    st.success("Using intelligent voice ranking system to select the highest quality voices available on your system.")
    
    # Enhanced voice detection with quality scoring
    st.write("**🔍 Voice Quality Analysis:**")
    voice_quality_js = """
    <script>
    function analyzeVoiceQuality() {
        const voices = window.speechSynthesis.getVoices();
        const italianVoices = voices.filter(v => v.lang.startsWith('it'));
        const englishVoices = voices.filter(v => v.lang.startsWith('en'));
        
        // Score all voices
        const scoredVoices = voices.map(voice => {
            let score = 0;
            const name = voice.name.toLowerCase();
            const lang = voice.lang.toLowerCase();
            
            // Ultra-premium voices
            if (name.includes('premium') || name.includes('enhanced') || name.includes('pro') || 
                name.includes('natural') || name.includes('human') || name.includes('real')) {
                score += 2000;
            }
            
            // High-quality platform voices
            if (name.includes('samantha') || name.includes('victoria') || name.includes('alex') || 
                name.includes('daniel') || name.includes('karen') || name.includes('tom') ||
                name.includes('fred') || name.includes('ralph') || name.includes('bruce') ||
                name.includes('jill') || name.includes('vicki') || name.includes('lee') ||
                name.includes('reed') || name.includes('susan') || name.includes('bells') ||
                name.includes('deranged') || name.includes('good news') || name.includes('bad news') ||
                name.includes('pipe organ') || name.includes('trinoids') || name.includes('whisper') ||
                name.includes('cellos') || name.includes('junior') || name.includes('senior') ||
                name.includes('boing') || name.includes('bahh') || name.includes('hysterical') ||
                name.includes('princess') || name.includes('rocko') || name.includes('wobble') ||
                name.includes('zarvox') || name.includes('david') || name.includes('zira') || 
                name.includes('mark') || name.includes('eva') || name.includes('helena') ||
                name.includes('jorge') || name.includes('pablo') || name.includes('miguel') ||
                name.includes('elena') || name.includes('hazel') || name.includes('heera') ||
                name.includes('kalpana') || name.includes('hemant') || name.includes('kalia') ||
                name.includes('neerja') || name.includes('priya') || name.includes('ravi') ||
                name.includes('sabina') || name.includes('tracy') || name.includes('yating') ||
                name.includes('yunyang') || name.includes('huihui') || name.includes('kangkang') ||
                name.includes('yaoyao') || name.includes('lili') || name.includes('hanhan') ||
                name.includes('zhiwei') || name.includes('asaf') || name.includes('hila') ||
                name.includes('heidi') || name.includes('irina') || name.includes('maria') ||
                name.includes('sapi') || name.includes('microsoft') || name.includes('google') ||
                name.includes('edge') || name.includes('chrome') || name.includes('chromium') ||
                name.includes('chiara') || name.includes('lucia') || name.includes('alice') ||
                name.includes('federica') || name.includes('marco') || name.includes('paolo') ||
                name.includes('roberto') || name.includes('silvia') || name.includes('giulia') ||
                name.includes('luca') || name.includes('anna') || name.includes('carlo') ||
                name.includes('giuseppe') || name.includes('antonio') || name.includes('francesca') ||
                name.includes('andrea')) {
                score += 1500;
            }
            
            // Language bonuses
            if (lang.startsWith('it')) score += 800;
            if (lang.startsWith('en')) score += 600;
            if (lang.startsWith('en-us')) score += 500;
            if (lang.startsWith('it-it')) score += 500;
            
            // Female voice bonus
            if (name.includes('female') || name.includes('woman') || name.includes('girl') ||
                name.includes('samantha') || name.includes('victoria') || name.includes('karen') ||
                name.includes('zira') || name.includes('eva') || name.includes('helena') ||
                name.includes('chiara') || name.includes('lucia') || name.includes('alice') ||
                name.includes('federica') || name.includes('silvia') || name.includes('elena') ||
                name.includes('giulia') || name.includes('anna') || name.includes('maria') ||
                name.includes('francesca') || name.includes('hazel') || name.includes('heera') ||
                name.includes('kalpana') || name.includes('neerja') || name.includes('priya') ||
                name.includes('sabina') || name.includes('tracy') || name.includes('yating') ||
                name.includes('huihui') || name.includes('yaoyao') || name.includes('lili') ||
                name.includes('hila') || name.includes('heidi') || name.includes('irina') ||
                name.includes('maria')) {
                score += 400;
            }
            
            // Avoid robotic voices
            if (name.includes('robot') || name.includes('mechanical') || name.includes('synthetic') ||
                name.includes('artificial') || name.includes('computer') || name.includes('system')) {
                score -= 1000;
            }
            
            return { name: voice.name, lang: voice.lang, score: score };
        });
        
        // Sort by score
        scoredVoices.sort((a, b) => b.score - a.score);
        
        // Find best voices for each language
        const bestItalian = scoredVoices.find(v => v.lang.startsWith('it'));
        const bestEnglish = scoredVoices.find(v => v.lang.startsWith('en'));
        
        console.log('🎯 ULTRA-HIGH-QUALITY VOICE ANALYSIS:');
        console.log('Top 10 voices:', scoredVoices.slice(0, 10).map(v => `${v.name} (${v.lang}) - Score: ${v.score}`));
        if (bestItalian) console.log('🏆 Best Italian:', bestItalian.name, 'Score:', bestItalian.score);
        if (bestEnglish) console.log('🏆 Best English:', bestEnglish.name, 'Score:', bestEnglish.score);
        console.log('Total voices available:', voices.length);
        
        return {
            total: voices.length,
            italian: italianVoices.length,
            english: englishVoices.length,
            bestItalian: bestItalian,
            bestEnglish: bestEnglish,
            topVoices: scoredVoices.slice(0, 10)
        };
    }
    
    if (window.speechSynthesis.getVoices().length === 0) {
        window.speechSynthesis.onvoiceschanged = analyzeVoiceQuality;
    } else {
        analyzeVoiceQuality();
    }
    </script>
    """
    components.html(voice_quality_js, height=0)
    
    st.info("🎯 Check browser console for voice quality analysis and best voice selection")
    
    # Voice quality tips
    st.write("**💡 Voice Quality Tips:**")
    st.markdown("""
    - **macOS**: Samantha, Victoria, Alex, Daniel
    - **Windows**: David, Zira, Mark, Eva, Helena
    - **Italian**: Chiara, Lucia, Alice, Federica
    - **Premium**: Any voice with 'Premium' or 'Enhanced' in name
    """)
    
    # Manual reload button
    if st.button("🔄 Reload TTS"):
        st.success("TTS will reload on next use")

# Language selection logic
if not st.session_state.language_selected:
    # Show language selection interface
    st.markdown("## 🇮🇹🇬🇧 Benvenuto! Welcome!")
    st.markdown("### Seleziona la tua lingua / Select your language")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🇮🇹 Italiano", use_container_width=True):
            st.session_state.last_lang = "it"
            st.session_state.language_selected = True
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("🇬🇧 English", use_container_width=True):
            st.session_state.last_lang = "en"
            st.session_state.language_selected = True
            st.session_state.chat_history = []
            st.rerun()
    
    # Show welcome message in both languages
    st.markdown("---")
    st.markdown("""
    ### 🇮🇹 Smart2t Course Chatbot
    Ciao! Sono il chatbot Smart2t. Posso aiutarti a trovare informazioni sui nostri corsi di formazione.
    Seleziona la tua lingua preferita per iniziare.
    
    ### 🇬🇧 Smart2t Course Chatbot  
    Hello! I'm the Smart2t chatbot. I can help you find information about our training courses.
    Select your preferred language to start.
    """)
    
    st.stop()  # Stop execution until language is selected

# Add hello message if chat is empty and language is selected
if not st.session_state.chat_history and st.session_state.language_selected:
    if st.session_state.last_lang == "it":
        hello_msg = "Ciao! Sono il chatbot Smart2t. Posso aiutarti a trovare informazioni sui nostri corsi. Chiedimi qualsiasi cosa sui corsi disponibili!"
    else:
        hello_msg = "Hello! I'm the Smart2t chatbot. I can help you find information about our courses. Ask me anything about available courses!"
    st.session_state.chat_history.append({"role": "assistant", "content": hello_msg})

# Display chat history (last 10 messages)
for i, msg in enumerate(st.session_state.chat_history[-10:]):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("time") is not None:
            st.caption(f"⏱️ Tempo di risposta: {msg['time']:.2f} secondi")
        
        if msg["role"] == "assistant":
            tts_controls(msg["content"], lang=st.session_state.last_lang, key=f"tts_{i}")
            # Mostra i bottoni di azione SOTTO i messaggi precedenti se c'è un corso attivo
            # e se questo è l'ultimo messaggio della cronologia
            is_last_message = (i == len(st.session_state.chat_history[-10:]) - 1)
            if is_last_message and st.session_state.current_course and not st.session_state.waiting_for_selection:
                st.markdown("---")
                col1, col2, col3= st.columns(3)
                with col1:
                    button_text_ask = "❓ Chiedi di questo corso" if st.session_state.last_lang == "it" else "❓ Ask about this course"
                    if st.button(button_text_ask, key=f"follow_up_btn_{i}", use_container_width=True):
                        msg_text = "Certo! Di quali informazioni specifiche hai bisogno?" if st.session_state.last_lang == "it" else "Sure! What specific information do you need?"
                        st.session_state.chat_history.append({"role": "assistant", "content": msg_text})
                        st.session_state.waiting_for_follow_up = True
                        st.rerun()
                with col2:
                    button_text_search = "🔍 Cerca altri corsi o poni altre domande" if st.session_state.last_lang == "it" else "🔍 Search other courses or ask other questions"
                    if st.button(button_text_search, key=f"new_search_btn_{i}", use_container_width=True):
                        msg_text = "Certamente! Digita le parole chiave." if st.session_state.last_lang == "it" else "Of course! Type the keywords."
                        st.session_state.chat_history.append({"role": "assistant", "content": msg_text})
                        st.session_state.current_course = None
                        st.session_state.waiting_for_follow_up = False
                        st.rerun()
                # --- NUOVO BLOCCO PER IL TERZO BOTTONE ---
                with col3:
                    # Mostra il bottone solo se c'è una lista a cui tornare
                    if st.session_state.last_course_list:
                        button_text_back = "🔙 Torna alla lista dei corsi" if st.session_state.last_lang == "it" else "🔙 Back to list"
                        if st.button(button_text_back, key=f"back_btn_{i}", use_container_width=True):
                            # Ripristina lo stato di selezione della lista
                            st.session_state.course_list = st.session_state.last_course_list
                            st.session_state.waiting_for_selection = True
                            st.session_state.current_course = None
                            
                            # Aggiunge un messaggio in chat per chiarezza
                            msg_text = "Ecco di nuovo la lista dei corsi trovati." if st.session_state.last_lang == "it" else "Here is the list of found courses again."
                            st.session_state.chat_history.append({"role": "assistant", "content": msg_text})
                            
                            st.rerun()

# Handle course selection list
if st.session_state.waiting_for_selection and st.session_state.course_list:
    with st.expander("Seleziona un corso per maggiori dettagli:", expanded=True):
        for i, (course_data, score) in enumerate(st.session_state.course_list):
            
            # Estrai il titolo in modo sicuro
            title = course_data.get('titolo', 'No title')
            
            # --- MODIFICA CHIAVE ---
            # Usa solo il titolo del corso come etichetta del bottone, senza il punteggio.
            button_label = title
            
            if st.button(button_label, key=f"course_select_{i}", use_container_width=True):
                selected_course_data = course_data
                selection_lang = st.session_state.last_lang

                # Messaggio per la cronologia chat
                user_selection_message = f"Ho selezionato: {title}" if selection_lang == "it" else f"I selected: {title}"
                st.session_state.chat_history.append({"role": "user", "content": user_selection_message})

                with st.spinner("Recupero info..."):
                    response = format_course(selected_course_data, selection_lang, llm=st.session_state.llm, user_query=f"info su {title}")
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                # Resetta lo stato dopo la selezione
                st.session_state.waiting_for_selection = False
                st.session_state.course_list = []
                st.session_state.current_course = selected_course_data
                st.rerun()

# Chat input
user_input = st.chat_input("Chiedi informazioni sui corsi (IT/EN):" if st.session_state.last_lang == "it" else "Ask about courses (IT/EN):")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    lang = st.session_state.last_lang
    response = ""
    course_list = []
    
    with st.spinner("Sto pensando..."):
        if st.session_state.current_course and st.session_state.waiting_for_follow_up:
            response = format_course(st.session_state.current_course, lang, llm=st.session_state.llm, user_query=user_input)
            st.session_state.waiting_for_follow_up = False
        elif st.session_state.current_course:
            if get_follow_up_decision(user_input, lang, st.session_state.llm, st.session_state.current_course):
                response = format_course(st.session_state.current_course, lang, llm=st.session_state.llm, user_query=user_input)
            else:
                response, course_list, _ = enhanced_chat(user_input, llm=st.session_state.llm, lang=lang)
        else:
            response, course_list, _ = enhanced_chat(user_input, llm=st.session_state.llm, lang=lang)

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    if course_list and len(course_list) > 1:
        st.session_state.waiting_for_selection = True
        st.session_state.course_list = course_list
        st.session_state.last_course_list = course_list
        st.session_state.current_course = None
    
    st.rerun()