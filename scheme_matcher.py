import os
import pandas as pd
import numpy as np
import pickle
import hashlib
import time
from typing import Dict, Any, List

class SchemeMatcherModule:
    def __init__(self, 
                 schemes_csv_path: str = "Government_schemes_final_english.csv",
                 embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
                 rasa_model_path: str = "models/rasa/nlu",
                 confidence_threshold: float = 0.5):
        self.schemes_csv_path = schemes_csv_path
        self.embedding_model_name = embedding_model
        self.rasa_model_path = rasa_model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.schemes_df = None
        self.scheme_embeddings = None
        self.column_mapping = {}
        self.csv_columns = []
        self.user_context = {}
        self.rasa_interpreter = None
        
        self.available = self._init_scheme_matcher()
        self._load_rasa_model()
    
    def _init_scheme_matcher(self) -> bool:
        try:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.embedding_model_name)
            except ImportError:
                self.model = None
            except Exception:
                self.model = None
            
            if not os.path.exists(self.schemes_csv_path):
                self._create_sample_schemes_csv()
            
            self.schemes_df = pd.read_csv(self.schemes_csv_path)
            self.csv_columns = self.schemes_df.columns.tolist()
            self._map_columns()
            
            if self.model is not None:
                self._compute_scheme_embeddings()
            
            return True
        except Exception:
            return False
    
    def _create_sample_schemes_csv(self):
        try:
            import csv
            sample_data = [
                ["Name", "Details", "Eligibility", "Benefits", "URL"],
                ["PM Kisan Samman Nidhi", "Financial assistance to farmers", "All small and marginal farmers", "₹6000 per year in three installments", "https://pmkisan.gov.in/"],
                ["Ayushman Bharat", "Health insurance scheme", "Poor and vulnerable families", "Health coverage up to ₹5 lakhs per family per year", "https://pmjay.gov.in/"],
                ["PM Awas Yojana", "Housing scheme", "Economically weaker sections", "Financial assistance for house construction", "https://pmaymis.gov.in/"]
            ]
            
            os.makedirs(os.path.dirname(self.schemes_csv_path) or '.', exist_ok=True)
            
            with open(self.schemes_csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(sample_data)
        except Exception:
            pass
    
    def _load_rasa_model(self):
        try:
            from rasa.nlu.model import Interpreter
            
            if os.path.exists(self.rasa_model_path) and os.path.isdir(self.rasa_model_path):
                self.rasa_interpreter = Interpreter.load(self.rasa_model_path)
        except Exception:
            pass
    
    def _map_columns(self):
        self.column_mapping = {}
        
        if 'Name' in self.csv_columns:
            self.column_mapping['scheme_name'] = 'Name'
        elif 'Department' in self.csv_columns:
            self.column_mapping['scheme_name'] = 'Department'
        
        if 'Details' in self.csv_columns:
            self.column_mapping['description'] = 'Details'
        
        if 'Eligibility' in self.csv_columns:
            self.column_mapping['eligibility'] = 'Eligibility'
        
        if 'Benefits' in self.csv_columns:
            self.column_mapping['benefits'] = 'Benefits'
        
        if 'URL' in self.csv_columns:
            self.column_mapping['url'] = 'URL'
    
    def _compute_scheme_embeddings(self):
        if not self.model or self.schemes_df is None:
            return
        
        csv_hash = self._calculate_csv_hash()
        cache_path = "scheme_embeddings.pkl"
        hash_path = "csv_hash.txt"
        
        if self._load_from_cache(cache_path, hash_path, csv_hash):
            return
        
        for attempt in range(3):
            try:
                self._compute_embeddings_directly()
                self._save_to_cache(cache_path, hash_path, csv_hash)
                break
            except Exception:
                if attempt == 2:
                    self.scheme_embeddings = None
                time.sleep(0.1)
    
    def _load_from_cache(self, cache_path, hash_path, csv_hash):
        if not os.path.exists(hash_path) or not os.path.exists(cache_path):
            return False
        
        try:
            with open(hash_path, 'r') as f:
                stored_hash = f.read().strip()
            
            if stored_hash != csv_hash:
                return False
            
            with open(cache_path, 'rb') as f:
                cached_embeddings = pickle.load(f)
                
            if (cached_embeddings is not None and 
                isinstance(cached_embeddings, np.ndarray) and 
                len(cached_embeddings) == len(self.schemes_df)):
                self.scheme_embeddings = cached_embeddings
                return True
                
        except Exception:
            pass
        
        return False
    
    def _save_to_cache(self, cache_path, hash_path, csv_hash):
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(self.scheme_embeddings, f)
            
            with open(hash_path, 'w') as f:
                f.write(csv_hash)
        except Exception:
            pass
    
    def _compute_embeddings_directly(self):
        try:
            scheme_texts = []
            for _, row in self.schemes_df.iterrows():
                combined_text = " ".join([
                    str(row.get(col, "")) 
                    for col in self.csv_columns 
                    if col in row and pd.notna(row[col])
                ])
                scheme_texts.append(combined_text)
            
            self.scheme_embeddings = self.model.encode(scheme_texts, show_progress_bar=False)
        except Exception:
            self.scheme_embeddings = None
    
    def _calculate_csv_hash(self) -> str:
        try:
            with open(self.schemes_csv_path, 'rb') as f:
                csv_data = f.read()
                return hashlib.sha256(csv_data).hexdigest()
        except Exception:
            return ""
    
    def set_user_context(self, name, occupation=None, location=None):
        self.user_context = {
            "name": name,
            "occupation": occupation,
            "location": location
        }
    
    def find_relevant_schemes(self, query, top_n=3):
        if not self.available or self.schemes_df is None:
            return []
        
        try:
            personalized_query = query
            if self.user_context.get("occupation"):
                personalized_query += f" for {self.user_context['occupation']}"
            if self.user_context.get("location"):
                personalized_query += f" in {self.user_context['location']}"
            
            if self.model is not None and self.scheme_embeddings is not None:
                try:
                    query_embedding = self.model.encode(personalized_query)
                    
                    query_embedding_norm = query_embedding / np.linalg.norm(query_embedding)
                    scheme_embeddings_norm = self.scheme_embeddings / np.linalg.norm(self.scheme_embeddings, axis=1, keepdims=True)
                    
                    similarities = np.dot(scheme_embeddings_norm, query_embedding_norm)
                    
                    results = []
                    top_indices = np.argsort(similarities)[::-1][:top_n * 2]
                    
                    for idx in top_indices:
                        similarity = similarities[idx]
                        
                        if similarity >= self.confidence_threshold:
                            scheme_info = self.schemes_df.iloc[idx].to_dict()
                            scheme_info['similarity_score'] = float(similarity)
                            results.append(scheme_info)
                    
                    results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
                    results = results[:top_n]
                    
                    if results:
                        return results
                except Exception:
                    pass
            
            return self._keyword_matching(personalized_query, top_n)
                
        except Exception:
            return self._keyword_matching(query, top_n)
    
    def _keyword_matching(self, query, top_n=3):
        if self.schemes_df is None:
            return []
            
        try:
            query_words = set(query.lower().split())
            results = []
            
            for _, row in self.schemes_df.iterrows():
                combined_text = " ".join([
                    str(row.get(col, "")) 
                    for col in self.csv_columns 
                    if col in row and pd.notna(row[col])
                ]).lower()
                
                matched_words = sum(1 for word in query_words if word in combined_text)
                if matched_words > 0:
                    similarity = matched_words / len(query_words)
                    if similarity >= self.confidence_threshold:
                        scheme_info = row.to_dict()
                        scheme_info['similarity_score'] = float(similarity)
                        results.append(scheme_info)
            
            results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
            return results[:top_n]
        except Exception:
            return []
    
    def parse_multi_intent_with_rasa(self, query):
        if self.rasa_interpreter is None:
            return []
        
        for _ in range(2):
            try:
                parsed = self.rasa_interpreter.parse(query)
                intents = [intent['name'] for intent in parsed.get('intent_ranking', []) 
                          if intent.get('confidence', 0) > 0.3]
                return intents
            except Exception:
                time.sleep(0.1)
                continue
        
        return []
    
    def handle_multi_intent_query(self, query, top_n=3):
        intents = self.parse_multi_intent_with_rasa(query)
        
        if not intents:
            return self.find_relevant_schemes(query, top_n)
            
        all_results = []
        for intent in intents:
            intent_results = self.find_relevant_schemes(intent, top_n=2)
            if intent_results:
                all_results.extend(intent_results)
                
        if not all_results:
            return self.find_relevant_schemes(query, top_n)
                
        unique_results = []
        seen_ids = set()
        for result in all_results:
            scheme_id = str(result.get(self.column_mapping.get("scheme_name", self.csv_columns[0]), ""))
            if scheme_id and scheme_id not in seen_ids:
                seen_ids.add(scheme_id)
                unique_results.append(result)
                
        unique_results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        return unique_results[:top_n]