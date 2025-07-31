NO_RESULT = {
    "en": "I'm sorry, I couldn't find a course that matches your request.",
    "it": "Mi dispiace, non ho trovato nessun corso corrispondente alla tua richiesta."
}

IDK_FIELD = {
    "en": "I'm sorry, I don't know the answer to that. This information is not available for the selected course.",
    "it": "Mi dispiace, non so rispondere a questa domanda. Questa informazione non è disponibile per il corso selezionato."
}

try:
    from markdownify import markdownify as md
except ImportError:
    import re
    def md(text):
        return re.sub(r'<[^>]+>', '', text) if text else text

def concise_summarize_course(fields, user_lang, llm=None, greet=True, user_message=""):
    if llm is None:
        try:
            from langchain_ollama import ChatOllama
            llm = ChatOllama(model="llama3", temperature=0.5)
        except ImportError:
            return "[Summarization unavailable: LLM not installed]"
    
    field_lines = []
    for k, v in fields.items():
        if v:
            field_lines.append(f"{k.capitalize()}: {v}")
    field_text = "\n".join(field_lines)
    
    user_message = user_message or ""
    
    # Check if user_message is just a number (course selection) or very short
    is_selection = len(user_message.strip()) <= 3 and user_message.strip().isdigit()
    
    if is_selection:
        # Provide general course summary for course selection
        prompt = f"""
IMPORTANT: Use ONLY the information provided below. DO NOT invent or add anything that is not present in the data.
Respond ONLY in {user_lang}. Do NOT use any other language.
Provide a comprehensive summary of this course including all available information.

IMPORTANT FIELD MAPPINGS:
- "Ore" = Duration of the course in hours
- "Costo" = Cost/Price of the course
- "Requisiti" = Requirements/Prerequisites
- "Descrizione" = Course description
- "Sede" = Location/Venue

Course information (use ONLY these data):
{field_text}

Provide a complete course summary in {user_lang} (strictly based on the provided data):
"""
    else:
        # Answer specific user question
        prompt = f"""
IMPORTANT: Use ONLY the information provided below. DO NOT invent or add anything that is not present in the data.
Respond ONLY in {user_lang}. Do NOT use any other language.
Be friendly and conversational, but do NOT add generic introductions or conclusions.

IMPORTANT FIELD MAPPINGS:
- "Ore" = Duration of the course in hours
- "Costo" = Cost/Price of the course  
- "Requisiti" = Requirements/Prerequisites
- "Descrizione" = Course description
- "Sede" = Location/Venue

Course information (use ONLY these data):
{field_text}

User message: {user_message}

Your response in {user_lang} (strictly based on the provided data):
"""
    
    try:
        result = llm.invoke(prompt)
        if hasattr(result, 'content'):
            response = result.content.strip()
        else:
            response = str(result).strip()
        return response
    except Exception as e:
        return f"[Summarization failed: {e}]"

FIELD_KEYWORDS = {
    "titolo": ["titolo", "title"],
    "descrizione": ["descrizione", "description"],
    "requisiti": [
        "requisiti", "requirements", "pre-requisiti", "pre request",
        "prerequisite", "pre requests", "prerequisites"
    ],
    "costo": ["costo", "cost", "prezzo", "price"],
    "testocosto": ["testocosto", "cost text", "price text"],
    "ore": ["ore", "hours", "durata", "duration"],
    "sede": ["sede", "address", "location", "luogo", "dove", "where", "place"]
}

import re
import difflib

def detect_requested_field(user_query):
    user_query = user_query.lower()
    for field, keywords in FIELD_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", user_query):
                return field
    words = re.findall(r'\w+', user_query)
    for field, keywords in FIELD_KEYWORDS.items():
        for word in words:
            match = difflib.get_close_matches(word, keywords, n=1, cutoff=0.8)
            if match:
                return field
    return None

GREETINGS = {
    "en": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "how are you"],
    "it": ["ciao", "salve", "buongiorno", "buonasera", "ehi", "come stai"]
}

def is_greeting(user_input, lang=None):
    user_input = user_input.lower().strip()
    for greet_list in GREETINGS.values():
        for greet in greet_list:
            if greet in user_input:
                return True
    return False

FRIENDLY_GREETING = {
    "en": "Hi there! 😊 I'm here to help you with any questions about our courses. How can I assist you today?",
    "it": "Ciao! 😊 Sono qui per aiutarti con qualsiasi domanda sui nostri corsi. Come posso aiutarti oggi?"
}

def add_natural_newlines(text):
    import re
    text = re.sub(r'(Cost:)', r'\n\1', text)
    text = re.sub(r'(After completing the course)', r'\n\1', text)
    text = re.sub(r'(If you have any questions)', r'\n\1', text)
    return text

def format_course(course, lang, llm=None, user_query=None):
    disclaimer = {
        "en": "\n\n*This is an automatic summary generated by AI. Some details may be best understood in the original language.*\n",
        "it": "\n\n*Questo è un riassunto automatico generato dall'IA. Alcuni dettagli potrebbero essere meglio compresi nella lingua originale.*\n"
    }
    disclaimer_text = disclaimer.get(lang, disclaimer["en"])
    requested_field = detect_requested_field(user_query or "")
    if requested_field:
        val = course.get(requested_field)
        val_md = md(str(val)) if val is not None and str(val).strip() else ""
        if not val_md:
            return IDK_FIELD[lang] + disclaimer_text
        summary = concise_summarize_course(
            {requested_field: val_md},
            "English" if lang == "en" else "Italian",
            llm=llm,
            greet=False,
            user_message=user_query or ""
        )
        label = requested_field.capitalize() if lang == "it" else FIELD_KEYWORDS[requested_field][0].capitalize()
        summary = add_natural_newlines(summary)
        return f"**{label}:**\n{summary}{disclaimer_text}"
    
    fields = {
        "titolo": md(str(course.get("titolo", ""))),
        "requisiti": md(str(course.get("requisiti", ""))),
        "costo": md(str(course.get("costo", ""))),
        "testocosto": md(str(course.get("testocosto", ""))),
        "ore": md(str(course.get("ore", ""))),
        "descrizione": md(str(course.get("descrizione", ""))),
        "sede": md(str(course.get("sede", ""))) if "sede" in course else ""
    }
    fields = {k: v for k, v in fields.items() if v}
    summary = concise_summarize_course(
        fields,
        "English" if lang == "en" else "Italian",
        llm=llm,
        greet=True,
        user_message=user_query or ""
    )
    summary = add_natural_newlines(summary)
    cost = course.get("costo")
    cost_line = ""
    if cost and str(cost).strip():
        if lang == "it":
            cost_line = f"\n**Costo:** {cost}"
        else:
            cost_line = f"\n**Cost:** {cost}"
    return f"{summary}{cost_line}{disclaimer_text}"

def format_response(results, lang, llm=None, user_query=None):
    if not results:
        return NO_RESULT[lang]
    if len(results) > 1:
        lines = []
        for i, course in enumerate(results, 1):
            title = course.get("titolo") or "(No title)"
            ore = course.get("ore")
            ore_str = f" ({ore} ore)" if ore else ""
            lines.append(f"{i}. {title}{ore_str}")
        choose_msg = {
            "en": "I found multiple courses matching your request. Please reply with the number of the course you want more details about:",
            "it": "Ho trovato più corsi che corrispondono alla tua richiesta. Rispondi con il numero del corso di cui vuoi maggiori dettagli:"
        }
        return choose_msg[lang] + "\n" + "\n".join(lines)
    return format_course(results[0], lang, llm=llm, user_query=user_query) 