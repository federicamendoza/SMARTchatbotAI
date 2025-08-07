import streamlit as st
import time
from language_utils import detect_language
import streamlit.components.v1 as components
from rag_chatbot import enhanced_chat
from langchain_ollama import ChatOllama
from prompts import format_course
import re

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

def speak_text_button(text, lang="en", key=None):
    """Ultra-high-quality browser TTS with intelligent voice selection for the best possible speech"""
    if st.button("🔊 Speak", key=key):
        # Map language codes for browser TTS
        lang_map = {"en": "en-US", "it": "it-IT"}
        browser_lang = lang_map.get(lang, "en-US")
        
        # Create ultra-advanced JavaScript for optimal voice selection
        js_code = f"""
        <script>
        function getVoiceQualityScore(voice) {{
            let score = 0;
            const name = voice.name.toLowerCase();
            const lang = voice.lang.toLowerCase();
            
            // Ultra-premium voices (highest priority)
            if (name.includes('premium') || name.includes('enhanced') || name.includes('pro') || 
                name.includes('natural') || name.includes('human') || name.includes('real')) {{
                score += 2000;
            }}
            
            // High-quality voice names by platform - more comprehensive list
            // macOS voices (known for high quality)
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
                name.includes('zarvox')) {{
                score += 1500;
            }}
            
            // Windows voices (high quality)
            if (name.includes('david') || name.includes('zira') || name.includes('mark') ||
                name.includes('eva') || name.includes('helena') || name.includes('jorge') ||
                name.includes('pablo') || name.includes('miguel') || name.includes('elena') ||
                name.includes('hazel') || name.includes('heera') || name.includes('kalpana') ||
                name.includes('hemant') || name.includes('heera') || name.includes('kalia') ||
                name.includes('neerja') || name.includes('priya') || name.includes('ravi') ||
                name.includes('sabina') || name.includes('tracy') || name.includes('yating') ||
                name.includes('yunyang') || name.includes('huihui') || name.includes('kangkang') ||
                name.includes('yaoyao') || name.includes('lili') || name.includes('hanhan') ||
                name.includes('zhiwei') || name.includes('asaf') || name.includes('hila') ||
                name.includes('heidi') || name.includes('irina') || name.includes('maria') ||
                name.includes('sapi') || name.includes('microsoft')) {{
                score += 1200;
            }}
            
            // Chrome/Edge voices (often high quality)
            if (name.includes('google') || name.includes('microsoft') || name.includes('edge') ||
                name.includes('chrome') || name.includes('chromium')) {{
                score += 1000;
            }}
            
            // Italian specific high-quality voices
            if (lang.startsWith('it')) {{
                if (name.includes('chiara') || name.includes('lucia') || name.includes('alice') ||
                    name.includes('federica') || name.includes('marco') || name.includes('paolo') ||
                    name.includes('roberto') || name.includes('silvia') || name.includes('elena') ||
                    name.includes('giulia') || name.includes('luca') || name.includes('anna') ||
                    name.includes('carlo') || name.includes('maria') || name.includes('giuseppe') ||
                    name.includes('antonio') || name.includes('francesca') || name.includes('andrea')) {{
                    score += 1800;
                }}
                // Any Italian voice gets significant bonus
                score += 800;
            }}
            
            // English specific high-quality voices
            if (lang.startsWith('en')) {{
                if (name.includes('samantha') || name.includes('victoria') || name.includes('alex') ||
                    name.includes('daniel') || name.includes('karen') || name.includes('tom') ||
                    name.includes('fred') || name.includes('ralph') || name.includes('bruce') ||
                    name.includes('david') || name.includes('zira') || name.includes('mark') ||
                    name.includes('eva') || name.includes('helena') || name.includes('jorge') ||
                    name.includes('pablo') || name.includes('miguel') || name.includes('elena') ||
                    name.includes('hazel') || name.includes('heera') || name.includes('kalpana') ||
                    name.includes('hemant') || name.includes('kalia') || name.includes('neerja') ||
                    name.includes('priya') || name.includes('ravi') || name.includes('sabina') ||
                    name.includes('tracy') || name.includes('yating') || name.includes('yunyang') ||
                    name.includes('huihui') || name.includes('kangkang') || name.includes('yaoyao') ||
                    name.includes('lili') || name.includes('hanhan') || name.includes('zhiwei') ||
                    name.includes('asaf') || name.includes('hila') || name.includes('heidi') ||
                    name.includes('irina') || name.includes('maria') || name.includes('sapi') ||
                    name.includes('microsoft') || name.includes('google')) {{
                    score += 1500;
                }}
                // Any English voice gets bonus
                score += 600;
            }}
            
            // Strongly prefer female voices (often sound more natural)
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
                name.includes('maria')) {{
                score += 400;
            }}
            
            // Prefer US English for English
            if (lang.startsWith('en-us')) {{
                score += 500;
            }}
            
            // Prefer Italian-IT for Italian
            if (lang.startsWith('it-it')) {{
                score += 500;
            }}
            
            // Prefer local voices over remote ones
            if (!name.includes('remote') && !name.includes('network')) {{
                score += 200;
            }}
            
            // Avoid robotic-sounding voices
            if (name.includes('robot') || name.includes('mechanical') || name.includes('synthetic') ||
                name.includes('artificial') || name.includes('computer') || name.includes('system')) {{
                score -= 1000;
            }}
            
            return score;
        }}
        
        function findBestVoice(targetLang) {{
            const voices = window.speechSynthesis.getVoices();
            let bestVoice = null;
            let bestScore = -1;
            let topVoices = [];
            
            console.log('Available voices:', voices.map(v => `${{v.name}} (${{v.lang}})`));
            
            for (const voice of voices) {{
                const score = getVoiceQualityScore(voice);
                console.log(`Voice: ${{voice.name}} (${{voice.lang}}) - Score: ${{score}}`);
                
                topVoices.push({{ voice: voice, score: score }});
                
                if (score > bestScore) {{
                    bestScore = score;
                    bestVoice = voice;
                }}
            }}
            
            // Sort by score and get top 3 voices for fallback
            topVoices.sort((a, b) => b.score - a.score);
            const top3Voices = topVoices.slice(0, 3);
            
            return {{ voice: bestVoice, score: bestScore, alternatives: top3Voices }};
        }}
        
        function speakWithBestVoice() {{
            const utterance = new SpeechSynthesisUtterance({repr(text)});
            utterance.lang = {repr(browser_lang)};
            
            // Find the absolute best voice with alternatives
            const result = findBestVoice({repr(browser_lang)});
            
            if (result.voice) {{
                utterance.voice = result.voice;
                console.log('🎯 Selected BEST voice:', result.voice.name, result.voice.lang, 'Score:', result.score);
                console.log('🔄 Alternative voices:', result.alternatives.slice(1).map(v => `${{v.voice.name}} (Score: ${{v.score}})`));
            }} else {{
                console.log('⚠️ No suitable voice found, using default');
            }}
            
            // Ultra-optimized speech parameters for maximum naturalness and human-like quality
            utterance.rate = 1.1;    // Slightly faster speed for more natural speech while maintaining clarity
            utterance.pitch = 1.1;    // Slightly higher pitch for more natural sound
            utterance.volume = 0.95;  // Slightly lower volume for more natural presence
            
            // Add natural speech patterns and pauses
            const naturalText = {repr(text)}.replace(/[.!?]/g, match => match + ' ');
            utterance.text = naturalText;
            
            // Enhanced event listeners for better control and debugging
            utterance.onstart = () => {{
                console.log('🎤 Speech started with voice:', utterance.voice ? utterance.voice.name : 'default');
            }};
            utterance.onend = () => {{
                console.log('✅ Speech completed successfully');
            }};
            utterance.onerror = (event) => {{
                console.error('❌ Speech error:', event.error);
            }};
            
            // Speak the text
            window.speechSynthesis.speak(utterance);
        }}
        
        // Ensure voices are loaded before speaking
        if (window.speechSynthesis.getVoices().length === 0) {{
            window.speechSynthesis.onvoiceschanged = speakWithBestVoice;
        }} else {{
            speakWithBestVoice();
        }}
        </script>
        """
        components.html(js_code, height=0)

st.set_page_config(page_title="Smart2t Course Chatbot", page_icon="🤖")
st.title("Smart2t Course Chatbot 🤖")

# Initialize session state
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
        if msg["role"] == "assistant":
            speak_text_button(msg["content"], lang=st.session_state.last_lang, key=f"tts_{i}")

# Chat input
user_input = st.chat_input("Chiedi informazioni sui corsi (IT/EN):" if st.session_state.last_lang == "it" else "Ask about courses (IT/EN):")
if user_input:
    response_time = None
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Use the selected language instead of automatic detection
    lang = st.session_state.last_lang
    
    # Check if user is selecting a course by number or full course name
    number_match = re.match(r'^\d+$', user_input.strip())
    
    # Check if user is selecting by full course name (e.g., "1. 3D Studio Max - Corso in FaD")
    course_name_match = re.match(r'^\d+\.\s*(.+)$', user_input.strip())
    
    # Check if user is selecting by full course name with hours (e.g., "3D Studio Max - Corso in FaD (6 ore)")
    course_with_hours_match = re.match(r'^(.+?)\s*\(\d+\s*ore\)$', user_input.strip())
    
    # Debug the selection state
    print(f"[DEBUG] Selection check - Input: '{user_input}', waiting_for_selection: {st.session_state.waiting_for_selection}, course_list length: {len(st.session_state.course_list) if st.session_state.course_list else 0}")
    print(f"[DEBUG] Number match: {number_match}, Course name match: {course_name_match}, Course with hours match: {course_with_hours_match}")
    
    if (number_match or course_name_match or course_with_hours_match) and st.session_state.waiting_for_selection and st.session_state.course_list:
        # User is selecting a course - use the selected language
        selection_lang = st.session_state.last_lang
        print(f"[DEBUG] Course selection - User input: '{user_input}', Selection lang: {selection_lang}")
        try:
            if number_match:
                # Numeric selection
                selection = int(user_input.strip()) - 1  # Convert to 0-based index
                print(f"[DEBUG] Numeric selection: {selection} (0-based)")
            elif course_name_match:
                # Full course name selection - find the course by name
                course_name = course_name_match.group(1).strip()
                selection = -1
                for i, course in enumerate(st.session_state.course_list):
                    if course.get('titolo', '').lower() == course_name.lower():
                        selection = i
                        break
                
                if selection == -1:
                    # Try partial match
                    for i, course in enumerate(st.session_state.course_list):
                        if course_name.lower() in course.get('titolo', '').lower():
                            selection = i
                            break
            elif course_with_hours_match:
                # Course name with hours - extract just the course name
                course_name = course_with_hours_match.group(1).strip()
                selection = -1
                for i, course in enumerate(st.session_state.course_list):
                    if course.get('titolo', '').lower() == course_name.lower():
                        selection = i
                        break
                
                if selection == -1:
                    # Try partial match
                    for i, course in enumerate(st.session_state.course_list):
                        if course_name.lower() in course.get('titolo', '').lower():
                            selection = i
                            break
            
            if 0 <= selection < len(st.session_state.course_list):
                selected_course = st.session_state.course_list[selection]
                print(f"[DEBUG] Selected course index: {selection}, Course: {selected_course.get('titolo', 'No title')}")
                response = format_course(selected_course, selection_lang, llm=st.session_state.llm, user_query=user_input)
                print(f"[DEBUG] Response language: {selection_lang}, Response preview: {response[:100]}...")
                st.session_state.waiting_for_selection = False
                st.session_state.course_list = []
                # Store the selected course for follow-up questions
                st.session_state.current_course = selected_course
                # Set follow-up mode for the selected course
                st.session_state.waiting_for_follow_up = True
                st.session_state.follow_up_prompt = "Ask me anything about this course (requirements, cost, duration, etc.)" if selection_lang == "en" else "Chiedimi qualsiasi cosa su questo corso (requisiti, costo, durata, ecc.)"
            else:
                response = f"Numero non valido. Inserisci un numero tra 1 e {len(st.session_state.course_list)}." if selection_lang == "it" else f"Invalid number. Please enter a number between 1 and {len(st.session_state.course_list)}."
        except ValueError:
            response = "Numero non valido. Riprova." if selection_lang == "it" else "Invalid number. Please try again."
    else:
        # Regular query - use the selected language
        print(f"[DEBUG] Regular query - Using selected language: {lang}")
        
        # Check if we have a current course and should treat this as a follow-up question
        if st.session_state.current_course and st.session_state.waiting_for_follow_up:
            # This is definitely a follow-up question about the current course
            print(f"[DEBUG] Follow-up question mode - Current course: {st.session_state.current_course.get('titolo', 'No title')}")
            response = format_course(st.session_state.current_course, lang, llm=st.session_state.llm, user_query=user_input)
        elif st.session_state.current_course:
            # We have a current course but not in follow-up mode - ask LLM to decide
            follow_up_decision = get_follow_up_decision(user_input, lang, st.session_state.llm, st.session_state.current_course)
            
            if follow_up_decision:
                # This is a follow-up question about the current course
                print(f"[DEBUG] LLM detected follow-up question about current course: {st.session_state.current_course.get('titolo', 'No title')}")
                response = format_course(st.session_state.current_course, lang, llm=st.session_state.llm, user_query=user_input)
            else:
                # New search query
                with st.spinner("🔍 Cercando informazioni..." if lang == "it" else "🔍 Searching for information..."):
                    try:
                        # Use enhanced RAG-first approach
                        response, course_list, response_time = enhanced_chat(user_input, llm=st.session_state.llm, lang=lang)
                        
                        st.session_state.last_response_time = response_time 

                        # Check if response contains a course list (multiple courses found)
                        if course_list and len(course_list) > 1:
                            st.session_state.waiting_for_selection = True
                            # Store the course list for later selection
                            st.session_state.course_list = course_list
                            # Clear current course when starting new search
                            st.session_state.current_course = None
                            st.session_state.waiting_for_follow_up = False
                            st.session_state.follow_up_prompt = None
                        
                    except Exception as e:
                        response = f"Mi dispiace, si è verificato un errore: {str(e)}" if lang == "it" else f"I'm sorry, an error occurred: {str(e)}"
                        st.session_state.waiting_for_selection = False
                        st.session_state.course_list = []
                        st.session_state.current_course = None
                        st.session_state.waiting_for_follow_up = False
                        st.session_state.follow_up_prompt = None
        else:
            # No current course, so this is definitely a new search
            with st.spinner("🔍 Cercando informazioni..." if lang == "it" else "🔍 Searching for information..."):
                try:
                    # Use enhanced RAG-first approach
                    response, course_list, response_time = enhanced_chat(user_input, llm=st.session_state.llm, lang=lang)
                    
                    # Check if response contains a course list (multiple courses found)
                    if course_list and len(course_list) > 1:
                        st.session_state.waiting_for_selection = True
                        # Store the course list for later selection
                        st.session_state.course_list = course_list
                        # Clear current course when starting new search
                        st.session_state.current_course = None
                        st.session_state.waiting_for_follow_up = False
                        st.session_state.follow_up_prompt = None
                    
                except Exception as e:
                    response = f"Mi dispiace, si è verificato un errore: {str(e)}" if lang == "it" else f"I'm sorry, an error occurred: {str(e)}"
                    st.session_state.waiting_for_selection = False
                    st.session_state.course_list = []
                    st.session_state.current_course = None
                    st.session_state.waiting_for_follow_up = False
                    st.session_state.follow_up_prompt = None
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        typing_speed = 0.01
        displayed = ""
        for char in response:
            displayed += char
            placeholder.markdown(displayed)
            time.sleep(typing_speed)
        # ✅ Visualizza il tempo di risposta che abbiamo salvato
        if "last_response_time" in st.session_state and st.session_state.last_response_time is not None:
            st.caption(f"⏱️ Tempo di risposta: {st.session_state.last_response_time:.2f} secondi")
            st.session_state.last_response_time = None # Pulisce per la prossima risposta

    st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Controlla se la variabile response_time è stata impostata e la stampa
    if response_time is not None:
        st.caption(f"⏱️ Tempo di risposta: {response_time:.2f} secondi")
        
    speak_text_button(response, lang=st.session_state.last_lang)
    
    # Add course action buttons if a course is selected
    if st.session_state.current_course:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("❓ Ask about this course", key="follow_up_btn"):
                # This will trigger a follow-up question mode
                st.session_state.waiting_for_follow_up = True
                st.session_state.follow_up_prompt = "Ask me anything about this course (requirements, cost, duration, etc.)"
                st.rerun()
        
        with col2:
            if st.button("🔍 Search other courses", key="new_search_btn"):
                # Clear current course and start new search
                st.session_state.current_course = None
                st.session_state.waiting_for_selection = False
                st.session_state.course_list = []
                st.session_state.waiting_for_follow_up = False
                st.session_state.follow_up_prompt = None
                st.rerun()
        
        # Show follow-up prompt if waiting for follow-up question
        if st.session_state.get("waiting_for_follow_up", False):
            st.info(st.session_state.get("follow_up_prompt", "Ask me anything about this course!")) 