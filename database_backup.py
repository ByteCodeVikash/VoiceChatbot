# database.py - Fixed CSV Database Integration
import sqlite3
import pandas as pd
import os
import hashlib
import json
from typing import List, Dict, Any, Optional
import logging
from rapidfuzz import fuzz, process
from synonym_dict import get_synonyms, enhance_search_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchemeDatabase:
    """Enhanced database for voice assistant with proper CSV integration"""
    
    def __init__(self, db_path: str, csv_path: str):
        self.db_path = db_path
        self.csv_path = csv_path
        self.csv_hash = self._get_csv_hash()
        
        # Initialize SQLite database
        self._initialize_sqlite()
        
        logger.info("✅ Database initialized successfully")
    
    def _get_csv_hash(self) -> str:
        """Get hash of CSV file for change detection"""
        if not os.path.exists(self.csv_path):
            return ""
        
        with open(self.csv_path, 'rb') as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()
    
    def _initialize_sqlite(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create schemes table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Department TEXT,
            Details TEXT,
            Benefits TEXT,
            Eligibility TEXT,
            Document_Required TEXT,
            Application_Process TEXT,
            Gender TEXT,
            Min_Age INTEGER,
            Max_Age INTEGER,
            Caste TEXT,
            Minority TEXT,
            URL TEXT,
            search_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create metadata table for tracking updates
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS database_metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        
        # Check if we need to reload data
        cursor.execute("SELECT value FROM database_metadata WHERE key = 'csv_hash'")
        stored_hash = cursor.fetchone()
        
        if not stored_hash or stored_hash[0] != self.csv_hash:
            logger.info("🔄 CSV changed, reloading database...")
            self._load_csv_data(conn)
            cursor.execute("""
            INSERT OR REPLACE INTO database_metadata (key, value) 
            VALUES ('csv_hash', ?)
            """, (self.csv_hash,))
            conn.commit()
        
        conn.close()
    
    def _load_csv_data(self, conn: sqlite3.Connection):
        """Load CSV data into SQLite"""
        if not os.path.exists(self.csv_path):
            logger.error(f"CSV file not found: {self.csv_path}")
            return
        
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM schemes")
        
        # Load CSV
        logger.info(f"📊 Loading CSV: {self.csv_path}")
        df = pd.read_csv(self.csv_path)
        
        logger.info(f"📋 CSV columns: {list(df.columns)}")
        logger.info(f"📈 Total schemes: {len(df)}")
        
        # Insert data
        for idx, row in df.iterrows():
            # Create comprehensive search text
            search_text = " ".join([
                str(row.get('Name', '')),
                str(row.get('Department', '')),
                str(row.get('Details', '')),
                str(row.get('Benefits', '')),
                str(row.get('Eligibility', '')),
                str(row.get('Gender', '')),
                str(row.get('Caste', '')),
                str(row.get('Minority', '')),
                str(row.get('Document_Required', ''))
            ]).lower()
            
            cursor.execute("""
            INSERT INTO schemes (
                Name, Department, Details, Benefits, Eligibility,
                Document_Required, Application_Process, Gender, Min_Age, Max_Age,
                Caste, Minority, URL, search_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get('Name', ''),
                row.get('Department', ''),
                row.get('Details', ''),
                row.get('Benefits', ''),
                row.get('Eligibility', ''),
                row.get('Document_Required', ''),
                row.get('Application_Process', ''),
                row.get('Gender', ''),
                row.get('Min Age', 0),
                row.get('Max Age', 100),
                row.get('Caste', ''),
                row.get('Minority', ''),
                row.get('URL', ''),
                search_text
            ))
        
        logger.info(f"✅ Loaded {len(df)} schemes into SQLite database")
    
    def search_by_context(self, query: str, occupation: str = None, 
                         location: str = None, top_k: int = 5) -> List[Dict]:
        """Enhanced search with context"""
        
        # Build enhanced query
        enhanced_query = enhance_search_query(query, occupation, location)
        search_terms = enhanced_query.lower().split()
        
        logger.info(f"🔍 Enhanced query: '{enhanced_query}'")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build search conditions
        conditions = []
        params = []
        
        for term in search_terms:
            if len(term) > 2:  # Skip very short terms
                conditions.append("search_text LIKE ?")
                params.append(f"%{term}%")
        
        # Add occupation-specific filters
        if occupation:
            occupation_terms = self._get_occupation_terms(occupation)
            for term in occupation_terms:
                conditions.append("search_text LIKE ?")
                params.append(f"%{term}%")
        
        # Build final query
        if conditions:
            where_clause = " OR ".join(conditions)
            sql = f"""
            SELECT * FROM schemes 
            WHERE {where_clause}
            ORDER BY 
                CASE 
                    WHEN LOWER(Name) LIKE ? THEN 1
                    WHEN LOWER(Department) LIKE ? THEN 2
                    WHEN LOWER(Benefits) LIKE ? THEN 3
                    ELSE 4
                END,
                LENGTH(Name)
            LIMIT ?
            """
            
            # Add ordering parameters
            primary_term = search_terms[0] if search_terms else query.lower()
            params.extend([f"%{primary_term}%", f"%{primary_term}%", f"%{primary_term}%", top_k * 2])
        else:
            # Fallback query for general search
            sql = """
            SELECT * FROM schemes 
            WHERE search_text LIKE ?
            ORDER BY LENGTH(Name)
            LIMIT ?
            """
            params = [f"%{query.lower()}%", top_k * 2]
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to results format
        results = []
        for row in rows:
            result = {
                'Name': row[1],
                'Department': row[2], 
                'Details': row[3],
                'Benefits': row[4],
                'Eligibility': row[5],
                'Document_Required': row[6],
                'Application_Process': row[7],
                'Gender': row[8],
                'Min_Age': row[9],
                'Max_Age': row[10],
                'Caste': row[11],
                'Minority': row[12],
                'URL': row[13],
                'Score': self._calculate_relevance_score(row, enhanced_query)
            }
            results.append(result)
        
        # Sort by relevance score
        results.sort(key=lambda x: x['Score'], reverse=True)
        
        logger.info(f"✅ Found {len(results)} results")
        
        # Debug: Print top results
        if results:
            for i, result in enumerate(results[:3], 1):
                logger.info(f"  {i}. {result['Name'][:50]}... (Score: {result['Score']:.2f})")
        
        return results[:top_k]
    
    def _get_occupation_terms(self, occupation: str) -> List[str]:
        """Get search terms for occupation"""
        occupation_map = {
            "farmer": ["agriculture", "farming", "crop", "kisan", "krishi", "खेती", "किसान"],
            "fisherman": ["fishing", "marine", "boat", "machhuara", "मछुआरा", "मत्स्य"],
            "women": ["women", "mahila", "female", "महिला", "lady"],
            "business": ["business", "entrepreneur", "mudra", "व्यवसाय", "udyog"],
            "student": ["education", "scholarship", "student", "शिक्षा", "छात्रवृत्ति"]
        }
        
        return occupation_map.get(occupation.lower(), [occupation])
    
    def _calculate_relevance_score(self, row: tuple, query: str) -> float:
        """Calculate relevance score"""
        name = str(row[1]).lower()
        department = str(row[2]).lower()
        benefits = str(row[4]).lower()
        
        query_lower = query.lower()
        
        # Name match gets highest score
        name_score = fuzz.partial_ratio(query_lower, name) / 100.0 * 0.5
        
        # Department match gets medium score
        dept_score = fuzz.partial_ratio(query_lower, department) / 100.0 * 0.3
        
        # Benefits match gets lower score
        benefits_score = fuzz.partial_ratio(query_lower, benefits) / 100.0 * 0.2
        
        return name_score + dept_score + benefits_score
    
    def search_schemes(self, query: str, limit: int = 10) -> List[Dict]:
        """Simple scheme search (backward compatibility)"""
        return self.search_by_context(query, top_k=limit)
    
    def get_scheme_count(self) -> int:
        """Get total number of schemes"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM schemes")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error getting scheme count: {e}")
            return 0
    
    def test_search(self, test_query: str = "farmer"):
        """Test search functionality"""
        logger.info(f"🧪 Testing search with query: '{test_query}'")
        results = self.search_by_context(test_query)
        
        if results:
            logger.info(f"✅ Test successful! Found {len(results)} results")
            for i, result in enumerate(results[:2], 1):
                logger.info(f"  {i}. {result['Name'][:60]}...")
        else:
            logger.warning("❌ Test failed - no results found")
        
        return results
    
    def close(self):
        """Close database connections"""
        # SQLite connections are closed after each operation
        pass

# Backward compatibility
EnhancedRAGDatabase = SchemeDatabase