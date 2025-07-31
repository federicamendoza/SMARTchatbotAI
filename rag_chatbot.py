import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from language_utils import detect_language
from prompts import format_response, NO_RESULT
from vector_utils import CourseVectorStore
from company_vector_store import CompanyVectorStore
import pandas as pd
import re

# --- Enhanced RAG-First Chat Function ---
def enhanced_chat(user_input, llm=None, lang=None):
   
    # Use provided language or fallback to detection
    if lang is None:
        lang = detect_language(user_input)
    
    # Step 1: Let LLM decide what to do with the query
    llm_decision = get_llm_decision(user_input, lang, llm)
    print(f"[LLM DECISION] {llm_decision}")
    
    # Step 2: Execute based on LLM decision
    if llm_decision == "general_conversation":
        return get_general_response(user_input, lang), None
    
    elif llm_decision == "company_info":
        return search_company_information(user_input, lang, llm), None
    
    elif llm_decision == "course_search":
        # Search database for courses using vector search only
        results = search_vector_database(user_input)
        
        if not results:
            return NO_RESULT[lang], None
        
        print(f"[RAG-FIRST] Found {len(results)} relevant results in database")
        
        # Let LLM format the response (course listing or single course)
        response = format_course_response_with_llm(results, lang, llm, user_input)
        return response, results if len(results) > 1 else None
    
    else:
        # Default fallback
        return get_general_response(user_input, lang), None

def get_llm_decision(user_input, lang, llm):
    
    decision_prompt = f"""
You are a smart assistant for Smart2t. Analyze the user's query and decide how to respond.

User query: "{user_input}"
Language: {lang}

Available options:
1. "general_conversation" - For greetings, thanks, identity questions, help requests
2. "company_info" - For questions about Smart2t company, location, services, certifications, contact info, phone number, email, address, headquarters, sede, telefono, contatti, or any company-related information
3. "course_search" - For questions about training courses, education, specific courses, software, skills, or any learning request

CRITICAL CLASSIFICATION RULES:
- If the user asks about ANY specific software, skill, technology, or learning topic, classify as "course_search"
- If the user asks about phone, phone number, contact, email, address, sede, telefono, contatti, company location, headquarters, or any company information, classify as "company_info"
- If the user asks about what courses are available, what you can learn, or any educational request, classify as "course_search"
- If the user asks about the company itself, its services, location, contact details, or any non-course information, classify as "company_info"

SPECIAL RULE FOR SINGLE WORDS:
- If the user types a single word or short phrase that could be a course topic, skill, or learning subject, ALWAYS classify as "course_search"
- Examples of single words that should be "course_search": sicurezza, python, design, excel, formazione, training, etc.
- Only classify as "company_info" if the single word is clearly about company contact/location (telefono, sede, email, etc.)

Examples:
- "Hi, who are you?" → general_conversation
- "Where is the company?" → company_info
- "What courses do you have?" → course_search
- "Tell me about Smart2t" → company_info
- "Security training" → course_search
- "sicurezza" → course_search (single word = course topic)
- "python" → course_search (single word = course topic)
- "excel" → course_search (single word = course topic)
- "formazione" → course_search (single word = course topic)
- "antincendio" → course_search (single word = course topic)
- "3d max" → course_search
- "Python programming" → course_search
- "AI courses" → course_search
- "Graphic design" → course_search
- "Do you have courses for..." → course_search
- "I want to learn..." → course_search
- "Training for..." → course_search
- "Corsi per..." → course_search
- "Formazione per..." → course_search
- "Thank you" → general_conversation
- "phone number" → company_info
- "telefono" → company_info (single word = contact info)
- "contatti" → company_info (single word = contact info)
- "email" → company_info (single word = contact info)
- "indirizzo" → company_info (single word = contact info)
- "sede" → company_info (single word = location)
- "where are you located" → company_info
- "contact information" → company_info
- "company address" → company_info

Respond with ONLY the decision (general_conversation, company_info, or course_search):
"""
    
    try:
        result = llm.invoke(decision_prompt)
        if hasattr(result, 'content'):
            decision = result.content.strip().lower()
        else:
            decision = str(result).strip().lower()
        
        # Clean up the response
        if "general_conversation" in decision:
            return "general_conversation"
        elif "company_info" in decision:
            return "company_info"
        elif "course_search" in decision:
            return "course_search"
        else:
            # Default to general conversation if unclear
            return "general_conversation"
            
    except Exception as e:
        print(f"[LLM DECISION ERROR] {e}")
        return "general_conversation"

def format_course_response_with_llm(results, lang, llm, user_input):
    """
    Return exactly 10 results with proper prioritization for exact matches.
    """
    # Take exactly 10 results
    top_results = results[:10]
    
    # Prioritize results that contain the exact search term
    user_input_lower = user_input.lower()
    prioritized_results = []
    other_results = []
    
    for course in top_results:
        title = course.get("titolo", "").lower()
        # Check if the search term appears in the title
        if user_input_lower in title:
            prioritized_results.append(course)
        else:
            other_results.append(course)
    
    # If we don't have enough prioritized results, check the full results list
    if len(prioritized_results) < 10:
        for course in results:
            if len(prioritized_results) >= 10:
                break
            title = course.get("titolo", "").lower()
            if user_input_lower in title and course not in prioritized_results:
                prioritized_results.append(course)
    
    # Combine prioritized results first, then others, but keep exactly 10
    final_results = prioritized_results + other_results
    final_results = final_results[:10]  # Keep exactly 10 results
    
    # DEBUG: Show what courses are being passed to LLM
    print(f"[DEBUG LLM INPUT] Top 10 courses (prioritized for '{user_input}'):")
    for i, course in enumerate(final_results, 1):
        title = course.get("titolo", "No title")
        print(f"  {i}. {title}")
    
    # Format the results as a numbered list
    lines = []
    for i, course in enumerate(final_results, 1):
        title = course.get("titolo") or "(No title)"
        ore = course.get("ore")
        ore_str = f" ({ore} ore)" if ore else ""
        lines.append(f"{i}. {title}{ore_str}")
    
    # Return the formatted results
    choose_msg = {
        "en": "Here are the top 10 courses from the search:",
        "it": "Ecco i primi 10 corsi dalla ricerca:"
    }
    response = choose_msg[lang] + "\n" + "\n".join(lines)
    print(f"[DEBUG SIMPLE OUTPUT] Response: {response[:200]}...")
    return response



def get_general_response(user_input, lang):
    
    user_input_lower = user_input.lower()
    
    # Greetings
    if any(word in user_input_lower for word in ["ciao", "salve", "buongiorno", "buonasera", "hi", "hello", "hey"]):
        if lang == "it":
            return "Ciao! Sono il chatbot di Smart Training & Technologies S.r.l. (S.T.& T.). Sono qui per aiutarti con informazioni sui nostri corsi di formazione e sulla nostra azienda. Come posso aiutarti oggi?"
        else:
            return "Hello! I'm the Smart Training & Technologies S.r.l. (S.T.& T.) chatbot. I'm here to help you with information about our training courses and our company. How can I help you today?"
    
    # Identity questions
    if any(word in user_input_lower for word in ["chi sei", "who are you", "cosa sei", "what are you"]):
        if lang == "it":
            return "Sono l'assistente virtuale di Smart Training & Technologies S.r.l. (S.T.& T.), un'azienda leader nella formazione professionale e nella consulenza per imprese, professionisti e pubbliche amministrazioni. Fondata nel 2015, siamo accreditati presso la Regione Piemonte e certificati ISO 9001:2015. Posso aiutarti a trovare il corso più adatto alle tue esigenze o fornirti informazioni sulla nostra azienda!"
        else:
            return "I'm Smart Training & Technologies S.r.l. (S.T.& T.)'s virtual assistant, a leading company in professional training and consulting for businesses, professionals and public administrations. Founded in 2015, we are accredited by the Piedmont Region and ISO 9001:2015 certified. I can help you find the course that best fits your needs or provide information about our company!"
    
    # Help questions
    if any(word in user_input_lower for word in ["aiuto", "help", "cosa puoi fare", "what can you do"]):
        if lang == "it":
            return "Posso aiutarti con informazioni sui nostri corsi di formazione e sulla nostra azienda! Chiedimi pure sui corsi disponibili, requisiti, costi, durata, o informazioni su Smart2t come sede (Torino), contatti, servizi, certificazioni, accreditamenti e molto altro."
        else:
            return "I can help you with information about our training courses and our company! Ask me about available courses, requirements, costs, duration, or information about Smart2t such as location (Turin), contacts, services, certifications, accreditations and much more."
    
    # Thanks
    if any(word in user_input_lower for word in ["grazie", "thank you", "thanks"]):
        if lang == "it":
            return "Prego! Sono qui per aiutarti. Se hai altre domande sui nostri corsi o sulla nostra azienda, non esitare a chiedere!"
        else:
            return "You're welcome! I'm here to help. If you have other questions about our courses or our company, don't hesitate to ask!"
    
    # Goodbye
    if any(word in user_input_lower for word in ["arrivederci", "goodbye", "bye", "a presto"]):
        if lang == "it":
            return "Arrivederci! È stato un piacere aiutarti. Torna pure quando vuoi per informazioni sui nostri corsi o sulla nostra azienda!"
        else:
            return "Goodbye! It was a pleasure helping you. Feel free to come back anytime for information about our courses or our company!"
    
    # Default response
    if lang == "it":
        return "Ciao! Sono l'assistente di Smart Training & Technologies S.r.l. (S.T.& T.). Posso aiutarti con informazioni sui nostri corsi di formazione e sulla nostra azienda. Chiedimi pure sui corsi disponibili, requisiti, costi, o informazioni su Smart2t come sede (Torino), contatti, servizi, certificazioni e accreditamenti!"
    else:
        return "Hello! I'm Smart Training & Technologies S.r.l. (S.T.& T.)'s assistant. I can help you with information about our training courses and our company. Ask me about available courses, requirements, costs, or information about Smart2t such as location (Turin), contacts, services, certifications and accreditations!"

def search_vector_database(user_input):
    """Search database using both semantic and syntactic approaches with smart prioritization"""
    try:
        store = CourseVectorStore()
        
        # Perform both semantic and syntactic searches
        semantic_results = store.semantic_query(user_input, top_k=15)
        syntactic_results = store.syntactic_query(user_input, top_k=15)
        
        print(f"[SEMANTIC SEARCH] Found {len(semantic_results)} semantic results")
        print(f"[SYNTACTIC SEARCH] Found {len(syntactic_results)} syntactic results")
        
        # DEBUG: Show the first 5 results from each approach
        print(f"[DEBUG SEMANTIC RESULTS] First 5 semantic results for '{user_input}':")
        for i, result in enumerate(semantic_results[:5], 1):
            title = result.get("titolo", "No title")
            print(f"  {i}. {title}")
        
        print(f"[DEBUG SYNTACTIC RESULTS] First 5 syntactic results for '{user_input}':")
        for i, result in enumerate(syntactic_results[:5], 1):
            title = result.get("titolo", "No title")
            print(f"  {i}. {title}")
        
        # Smart combination with scoring system
        user_input_lower = user_input.lower().strip()
        user_words = set(user_input_lower.split())
        
        # Dynamically identify important keywords based on word characteristics
        def identify_important_words(words, all_course_titles):
            """Dynamically identify important words based on rarity and specificity"""
            important_words = set()
            
            # Get all course titles for frequency analysis
            all_titles_text = " ".join(all_course_titles).lower()
            all_title_words = set(all_titles_text.split())
            
            for word in words:
                # Skip very common words
                if len(word) < 3:
                    continue
                    
                # Calculate word importance score
                importance_score = 0
                
                # 1. Length bonus (longer words are usually more specific)
                importance_score += len(word) * 2
                
                # 2.Rarity bonus (words that appear in fewer courses are more specific)
                word_frequency = sum(1 for title in all_course_titles if word in title.lower())
                if word_frequency > 0:
                    rarity_score = max(1, 50 - word_frequency)  # Higher score for rarer words
                    importance_score += rarity_score
                
                # 3. Technical/specific word patterns
                if any(pattern in word for pattern in ['ing', 'zione', 'mento', 'ismo', 'logia', 'grafia']):
                    importance_score += 30
                
                # 4. Capitalization in original query (indicates importance)
                original_word = next((w for w in user_input.split() if w.lower() == word), word)
                if original_word[0].isupper():
                    importance_score += 20
                
                # 5. Domain-specific patterns
                domain_patterns = ['corso', 'formazione', 'aggiornamento', 'training', 'certificazione']
                if word in domain_patterns:
                    importance_score += 15
                
                # 6. Technical terms (words with numbers, special characters, or technical suffixes)
                if any(char.isdigit() for char in word) or any(char in word for char in ['-', '_', '/']):
                    importance_score += 25
                
                # Add to important words if score is high enough
                if importance_score >= 40:  # Threshold for importance
                    important_words.add(word)
            
            return important_words
        
        # Get all course titles for frequency analysis
        all_course_titles = []
        for result in semantic_results + syntactic_results:
            title = result.get("titolo", "")
            if title:
                all_course_titles.append(title)
        
        # Dynamically identify important keywords
        important_keywords = identify_important_words(user_words, all_course_titles)
        
        print(f"[DYNAMIC KEYWORDS] Identified important words: {important_keywords}")
        
        # Score and combine results
        scored_results = []
        seen_titles = set()
        
        # Score syntactic results (higher priority for keyword matches)
        for i, result in enumerate(syntactic_results):
            title = result.get("titolo", "").lower()
            if title not in seen_titles:
                score = 0
                
                # Base score for syntactic match
                score += 100
                
                # Enhanced keyword matching with partial word support
                for word in user_words:
                    if word in title:
                        score += 50
                        # Extra bonus for longer/more specific words
                        if len(word) > 3:
                            score += 20
                        # Extra bonus for important keywords
                        if word in important_keywords:
                            score += 30
                    # Check for partial matches (word is part of a longer word in title)
                    elif any(word in title_word for title_word in title.split()):
                        score += 30
                        if word in important_keywords:
                            score += 20
                
                # Bonus for position (earlier results get higher scores, but reduced penalty)
                score += (15 - i) * 1  # Reduced from 2 to 1
                
                # Bonus for exact phrase match
                if user_input_lower in title:
                    score += 100
                
                # Extra bonus for courses that contain multiple search terms
                matching_words = sum(1 for word in user_words if word in title or any(word in title_word for title_word in title.split()))
                if matching_words > 1:
                    score += matching_words * 25
                
                scored_results.append((score, result, "syntactic"))
                seen_titles.add(title)
        
        # Score semantic results
        for i, result in enumerate(semantic_results):
            title = result.get("titolo", "").lower()
            if title not in seen_titles:
                score = 0
                
                # Base score for semantic match
                score += 50
                
                # Enhanced keyword matching for semantic results too
                for word in user_words:
                    if word in title:
                        score += 30
                        if len(word) > 3:
                            score += 10
                        if word in important_keywords:
                            score += 20
                    # Check for partial matches
                    elif any(word in title_word for title_word in title.split()):
                        score += 20
                        if word in important_keywords:
                            score += 15
                
                # Bonus for position
                score += (15 - i) * 1
                
                # Bonus for exact phrase match
                if user_input_lower in title:
                    score += 80
                
                # Extra bonus for courses that contain multiple search terms
                matching_words = sum(1 for word in user_words if word in title or any(word in title_word for title_word in title.split()))
                if matching_words > 1:
                    score += matching_words * 15
                
                scored_results.append((score, result, "semantic"))
                seen_titles.add(title)
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # Take top 10 results
        final_results = [result for score, result, source in scored_results[:10]]
        
        print(f"[SMART COMBINATION] Final results with scores:")
        for i, (score, result, source) in enumerate(scored_results[:10], 1):
            title = result.get("titolo", "No title")
            print(f"  {i}. [{source.upper()}] Score: {score} - {title}")
        
        print(f"[COMBINED RESULTS] Total unique results: {len(final_results)}")
        return final_results
        
    except Exception as e:
        print(f"[VECTOR SEARCH ERROR] {e}")
        return []

def format_course_with_llm(course, lang, llm, user_input):
    """
    Format course information using LLM but only with actual database data.
    Prevents hallucination by constraining LLM to work only with retrieved information.
    """
    from prompts import format_course
    return format_course(course, lang, llm, user_input)

def search_company_information(user_input, lang, llm):
    """
    Search and format company information using LLM decision making.
    """
    # Direct fallback for address/location queries in Italian
    address_keywords_it = ["sede", "dove si trova", "indirizzo", "dov'è", "dove si trova l'azienda", "dove siete", "dove siete situati", "dove posso trovarvi"]
    if lang == "it" and any(kw in user_input.lower() for kw in address_keywords_it):
        return "La sede principale di Smart2t è: Corso Siracusa 10, 10136 Torino (TO), Italia."
    address_keywords_en = ["address", "location", "where is the company", "where are you located", "where can I find you", "headquarters"]
    if lang == "en" and any(kw in user_input.lower() for kw in address_keywords_en):
        return "The main office of Smart2t is: Corso Siracusa 10, 10136 Torino (TO), Italy."
    try:
        company_store = CompanyVectorStore()
        results = company_store.query(user_input)
        
        if not results:
            if lang == "it":
                return "Mi dispiace, non ho trovato informazioni specifiche su quello che stai cercando. Puoi contattarci direttamente al +39 011 800 64 46 o via email info@smart2t.it per maggiori informazioni."
            else:
                return "I'm sorry, I couldn't find specific information about what you're looking for. You can contact us directly at +39 011 800 64 46 or via email info@smart2t.it for more information."
        
        # Let LLM format the company information response
        return format_company_response_with_llm(results, lang, llm, user_input)
        
    except Exception as e:
        print(f"[COMPANY SEARCH ERROR] {e}")
        if lang == "it":
            return "Mi dispiace, si è verificato un errore nella ricerca delle informazioni aziendali. Puoi contattarci direttamente al +39 011 800 64 46."
        else:
            return "I'm sorry, an error occurred while searching for company information. You can contact us directly at +39 011 800 64 46."

def format_company_response_with_llm(results, lang, llm, user_input):
    """
    Let LLM format company information response. Enforce strict language output and explicit address copying.
    """
    # Prepare the information for LLM formatting
    info_text = ""
    for result in results:
        if result["type"] == "vector_search":
            info_text += result["content"] + "\n\n"
        else:
            info_text += result["content"] + "\n\n"
    
    # Use LLM to format the response
    prompt = f"""
You are a helpful assistant for Smart2t. The user asked: "{user_input}"

IMPORTANT RULES:
1. Respond ONLY in {lang} language. DO NOT use any other language.
2. Use ONLY the company information provided below
3. Be friendly, helpful and conversational
4. Do not invent any information not in the data
5. If the user asks about location or address, ALWAYS copy and paste the address exactly as provided below. Do NOT say '[inserisci l'indirizzo esatto]'.
6. If the user asks about contact info, provide the phone and email
7. If the user asks about services, list the main services offered

Company information (use ONLY these data):
{info_text}

If the user asks for the address, always copy the address exactly as provided above. Provide a helpful response in {lang} based on the user's question. DO NOT use any other language:
"""
    
    try:
        result = llm.invoke(prompt)
        if hasattr(result, 'content'):
            response = result.content.strip()
        else:
            response = str(result).strip()
        return response
    except Exception as e:
        print(f"[LLM COMPANY FORMATTING ERROR] {e}")
        # Fallback response
        if results:
            if lang == "it":
                return results[0]["content"] + "\n(Questa risposta è stata generata automaticamente in italiano.)"
            else:
                return results[0]["content"] + "\n(This response was automatically generated in English.)"
        else:
            if lang == "it":
                return "Mi dispiace, non sono riuscito a formattare la risposta. Contattaci direttamente per maggiori informazioni."
            else:
                return "I'm sorry, I couldn't format the response. Please contact us directly for more information."

# --- Legacy chat function for backward compatibility ---
def chat(user_input, llm=None):
    """Legacy chat function - now uses enhanced RAG-first approach with vector search only"""
    return enhanced_chat(user_input, llm)

if __name__ == "__main__":
    print("Enhanced RAG-First mode with vector search only.")
    llm = ChatOllama(model="llama3", base_url="http://localhost:11434")
    while True:
        user_input = input("You: ")
        response, course_list = enhanced_chat(user_input, llm=llm)
        print("Bot:", response)
        if course_list:
            print("Course List:", course_list)
