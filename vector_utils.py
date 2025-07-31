from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import os
import pickle
import numpy as np
import faiss
import mysql.connector
import re

FAISS_INDEX_PATH = "faiss_index.bin"
COURSES_META_PATH = "courses.pkl"

def fetch_courses_dict():
    """Fetch courses directly from database"""
    try:
        conn = mysql.connector.connect(
            host="smartoltre.nanoh.it",
            port=3306,
            user="ufficio",
            password="2ksVkoEPF0DNrKT",
            database="smart"
        )
        cursor = conn.cursor(dictionary=True)
        
        # Fetch courses with stato_id != 4
        sql_query = """
        SELECT titolo, descrizione, requisiti, costo, testocosto, ore
        FROM corsi 
        WHERE stato_id != 4
        ORDER BY titolo
        """
        
        cursor.execute(sql_query)
        courses = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return courses
    except Exception as e:
        print(f"[VECTOR STORE ERROR] Failed to fetch courses: {e}")
        return []

class CourseVectorStore:
    def __init__(self, model_name="all-mpnet-base-v2", force_rebuild=False):
        self.model = SentenceTransformer(model_name)
        if not force_rebuild and os.path.exists(FAISS_INDEX_PATH) and os.path.exists(COURSES_META_PATH):
            self._load()
        else:
            self.courses = fetch_courses_dict()
            self.embeddings = self._embed_courses()
            self._build_faiss()
            self._save()

    def _embed_courses(self):
        texts = []
        for course in self.courses:
            # Use only the course title for embedding
            course_text = []
            if course.get("titolo"):
                course_text.append(str(course["titolo"]))
            texts.append(" ".join(course_text))
        
        return self.model.encode(texts, show_progress_bar=False)

    def _build_faiss(self):
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(np.array(self.embeddings).astype(np.float32))

    def _save(self):
        faiss.write_index(self.index, FAISS_INDEX_PATH)
        with open(COURSES_META_PATH, "wb") as f:
            pickle.dump(self.courses, f)

    def _load(self):
        self.index = faiss.read_index(FAISS_INDEX_PATH)
        with open(COURSES_META_PATH, "rb") as f:
            self.courses = pickle.load(f)

    def semantic_query(self, user_query, top_k=20):
        """Semantic search using vector embeddings"""
        query_emb = self.model.encode([user_query])
        D, I = self.index.search(np.array(query_emb).astype(np.float32), top_k)
        
        results = []
        for idx, dist in zip(I[0], D[0]):
            results.append(self.courses[idx])
        
        return results

    def syntactic_query(self, user_query, top_k=20):
        """Syntactic search using exact matching, substring matching, and word-based matching"""
        query_lower = user_query.lower().strip()
        query_words = query_lower.split()
        
        results = []
        scores = []  # Lower score = better match
        
        for course in self.courses:
            titolo = str(course.get("titolo", "")).lower()
            title_words = titolo.split()
            
            score = float('inf')  # Higher score = worse match
            
            # 1. Exact match (best score: 0)
            if query_lower == titolo:
                score = 0
            
            # 2. Query is exact substring of title (score: 1)
            elif query_lower in titolo:
                score = 1
            
            # 3. Title starts with query (score: 2)
            elif titolo.startswith(query_lower):
                score = 2
            
            # 4. Title ends with query (score: 3)
            elif titolo.endswith(query_lower):
                score = 3
            
            # 5. All query words found in title (score: 4 + number of extra words)
            elif len(query_words) > 1:
                matching_words = sum(1 for word in query_words if any(word in title_word for title_word in title_words))
                if matching_words == len(query_words):  # All words match
                    extra_words = len(title_words) - len(query_words)
                    score = 4 + extra_words
            
            # 6. At least 2 query words match (score: 10 + number of missing words)
            elif len(query_words) > 1:
                matching_words = sum(1 for word in query_words if any(word in title_word for title_word in title_words))
                if matching_words >= 2:
                    missing_words = len(query_words) - matching_words
                    score = 10 + missing_words
            
            # 7. At least 1 word matches (score: 20 + number of missing words)
            else:
                matching_words = sum(1 for word in query_words if any(word in title_word for title_word in title_words))
                if matching_words >= 1:
                    missing_words = len(query_words) - matching_words
                    score = 20 + missing_words
            
            # 8. Fuzzy matching for typos (score: 30 + edit distance)
            if score == float('inf'):
                # Check if any query word is similar to any title word
                for query_word in query_words:
                    for title_word in title_words:
                        # Simple similarity check (words that share most characters)
                        if len(query_word) > 3 and len(title_word) > 3:
                            # Check if words are similar (at least 70% character overlap)
                            common_chars = sum(1 for c in query_word if c in title_word)
                            similarity = common_chars / max(len(query_word), len(title_word))
                            if similarity >= 0.7:
                                score = 30 + (1 - similarity) * 10
                                break
                    if score != float('inf'):
                        break
            
            # Add to results if we found a match
            if score != float('inf'):
                results.append(course)
                scores.append(score)
        
        # Sort by score (lower is better) and return top_k
        if results:
            sorted_pairs = sorted(zip(results, scores), key=lambda x: x[1])
            results = [course for course, score in sorted_pairs[:top_k]]
        
        return results

    def query(self, user_query, top_k=20):
        """Legacy method - returns semantic search results for backward compatibility"""
        return self.semantic_query(user_query, top_k) 