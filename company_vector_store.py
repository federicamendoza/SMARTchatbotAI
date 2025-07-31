"""
Company Information Vector Store
This module creates and manages a vector store for company information
that can be searched using semantic similarity.
"""

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os
from company_info import get_company_info_text, search_company_info

class CompanyVectorStore:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initialize the company vector store.
        """
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.texts = []
        self.index_file = "company_index.bin"
        self.texts_file = "company_texts.pkl"
        
        # Load or create the vector store
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """
        Load existing index or create a new one.
        """
        if os.path.exists(self.index_file) and os.path.exists(self.texts_file):
            print("[COMPANY VECTOR STORE] Loading existing index...")
            self._load_index()
        else:
            print("[COMPANY VECTOR STORE] Creating new index...")
            self._create_index()
    
    def _create_index(self):
        """
        Create a new vector index from company information.
        """
        # Get company information text
        company_text = get_company_info_text()
        
        # Split into chunks for better search
        chunks = self._split_text_into_chunks(company_text)
        self.texts = chunks
        
        # Create embeddings
        embeddings = self.model.encode(chunks, show_progress_bar=True)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.index.add(embeddings.astype('float32'))
        
        # Save index and texts
        self._save_index()
        print(f"[COMPANY VECTOR STORE] Created index with {len(chunks)} chunks")
    
    def _split_text_into_chunks(self, text, max_length=200):
        """
        Split text into chunks for better vectorization.
        """
        sentences = text.split('\n')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _save_index(self):
        """
        Save the FAISS index and texts to disk.
        """
        faiss.write_index(self.index, self.index_file)
        with open(self.texts_file, 'wb') as f:
            pickle.dump(self.texts, f)
    
    def _load_index(self):
        """
        Load the FAISS index and texts from disk.
        """
        self.index = faiss.read_index(self.index_file)
        with open(self.texts_file, 'rb') as f:
            self.texts = pickle.load(f)
    
    def query(self, query_text, top_k=3):
        """
        Search for relevant company information.
        """
        # First try direct search for specific information
        direct_results = search_company_info(query_text)
        if direct_results:
            return direct_results
        
        # If no direct results, use vector search
        query_embedding = self.model.encode([query_text])
        
        # Search the index
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if score > 0.3:  # Similarity threshold
                results.append({
                    "type": "vector_search",
                    "content": self.texts[idx],
                    "score": float(score),
                    "source": "company_info"
                })
        
        return results
    
    def get_company_overview(self):
        """
        Get a comprehensive overview of the company.
        """
        from company_info import COMPANY_INFO
        
        overview = {
            "name": COMPANY_INFO["company_name"],
            "description": COMPANY_INFO["description"],
            "mission": COMPANY_INFO["mission"],
            "vision": COMPANY_INFO["vision"],
            "founded": COMPANY_INFO["founded"],
            "headquarters": COMPANY_INFO["headquarters"],
            "services": COMPANY_INFO["services"][:5],  # Top 5 services
            "contact": {
                "phone": COMPANY_INFO["headquarters"]["phone"],
                "email": COMPANY_INFO["headquarters"]["email"],
                "website": COMPANY_INFO["headquarters"]["website"]
            }
        }
        
        return overview 