#!/usr/bin/env python3
# debug_rag_response.py - Debug RAG response in voice assistant context

from enhanced_rag_database import EnhancedRAGDatabase, answer_schemes_question

def debug_voice_assistant_rag():
    """Debug exactly what voice assistant is getting"""
    
    print("🔍 Debugging Voice Assistant RAG Response")
    print("=" * 60)
    
    # Initialize RAG system exactly like voice assistant
    groq_key = "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"
    csv_path = "Government_schemes_final_english.csv"
    
    # Create RAG database instance
    rag_db = EnhancedRAGDatabase(csv_path, groq_key)
    
    if not rag_db.available:
        print("❌ RAG Database not available")
        return
    
    print("✅ RAG Database initialized")
    
    # Test queries exactly like voice assistant
    test_cases = [
        {
            "query": "show me agriculture scheme for farmers",
            "occupation": "farmer", 
            "location": None
        },
        {
            "query": "what schemes are available for women",
            "occupation": "women",
            "location": None
        },
        {
            "query": "how can I get seeds and fertilizers for free during Krushi Mahotsav in Gujarat",
            "occupation": "farmer",
            "location": "gujarat"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*15} Test Case {i} {'='*15}")
        query = test_case["query"]
        occupation = test_case["occupation"]
        location = test_case["location"]
        
        print(f"Query: {query}")
        print(f"Occupation: {occupation}")
        print(f"Location: {location}")
        print("-" * 50)
        
        # Step 1: Test search_by_context (what voice assistant calls)
        print("🔍 Step 1: Testing search_by_context...")
        results = rag_db.search_by_context(query, occupation, location, top_k=3)
        
        if results:
            print(f"✅ Found {len(results)} results:")
            for j, result in enumerate(results, 1):
                name = result.get('Name', 'Unknown')
                details = result.get('Details', 'No details')
                print(f"  {j}. Name: {name[:80]}...")
                print(f"     Details: {details[:100]}...")
                print()
        else:
            print("❌ No results from search_by_context")
            continue
        
        # Step 2: Test direct answer function
        print("🔍 Step 2: Testing direct answer_schemes_question...")
        
        # Build enhanced query like voice assistant does
        enhanced_query = query
        if occupation:
            enhanced_query += f" for {occupation}"
        if location:
            enhanced_query += f" in {location}"
        
        print(f"Enhanced query: {enhanced_query}")
        
        direct_answer = answer_schemes_question(enhanced_query)
        print(f"Direct answer: {direct_answer}")
        print()
        
        # Step 3: Show what voice assistant would format
        print("🔍 Step 3: Voice assistant response formatting...")
        
        # Simulate voice assistant format_scheme_response logic
        if direct_answer and len(direct_answer.strip()) > 20:
            import re
            cleaned_answer = re.sub(r'[<>{}*#]', '', direct_answer)
            
            if len(cleaned_answer) > 200:
                sentences = cleaned_answer.split('.')
                if len(sentences) >= 2:
                    voice_response = sentences[0] + '. ' + sentences[1] + '.'
                else:
                    voice_response = sentences[0] + '.'
            else:
                voice_response = cleaned_answer
            
            print(f"Voice Response: {voice_response}")
        else:
            print("❌ No proper voice response generated")
        
        print("\n" + "="*60)

def test_exact_voice_assistant_flow():
    """Test the exact flow that voice assistant uses"""
    
    print("\n🎯 Testing Exact Voice Assistant Flow")
    print("=" * 60)
    
    # Simulate voice assistant initialization
    from config import CONFIG
    
    groq_api_key = CONFIG.get("GROQ_API_KEY", "")
    if not groq_api_key:
        import json
        try:
            with open("config.json") as f:
                config_data = json.load(f)
                groq_api_key = config_data.get("GROQ_API_KEY", "")
        except:
            pass
    
    # Initialize like voice assistant
    scheme_db = EnhancedRAGDatabase(
        csv_path=CONFIG["schemes_csv_path"],
        groq_api_key=groq_api_key
    )
    
    if not scheme_db.available:
        print("❌ Voice assistant RAG not available")
        return
    
    print("✅ Voice assistant RAG initialized")
    
    # Test context
    user_context = {
        "occupation": "farmer",
        "location": None
    }
    
    query = "show me agriculture scheme for farmers"
    
    print(f"\nTesting query: {query}")
    print(f"User context: {user_context}")
    
    # Step 1: Find relevant schemes (like voice assistant does)
    occupation = user_context.get("occupation")
    location = user_context.get("location")
    
    print(f"\n🔍 Calling search_by_context with:")
    print(f"  Query: {query}")
    print(f"  Occupation: {occupation}")
    print(f"  Location: {location}")
    
    relevant_schemes = scheme_db.search_by_context(query, occupation, location, top_k=5)
    
    if relevant_schemes:
        print(f"\n✅ Found {len(relevant_schemes)} schemes:")
        for i, scheme in enumerate(relevant_schemes, 1):
            name = scheme.get('Name', 'Unknown')
            score = scheme.get('Score', 0)
            details = scheme.get('Details', 'No details')
            print(f"  {i}. {name[:50]}... (Score: {score:.3f})")
            print(f"     Details: {details[:80]}...")
    else:
        print("❌ No schemes found")
        return
    
    # Step 2: Format response (like voice assistant does)
    print(f"\n🔍 Formatting response...")
    
    try:
        # Build enhanced query
        enhanced_query = query
        if occupation:
            enhanced_query += f" for {occupation}"
        if location:
            enhanced_query += f" in {location}"
        
        print(f"Enhanced query for answer: {enhanced_query}")
        
        # Get detailed answer from RAG
        detailed_answer = answer_schemes_question(enhanced_query)
        
        print(f"Raw RAG answer: {detailed_answer}")
        
        if detailed_answer and len(detailed_answer.strip()) > 20:
            # Clean and format for voice
            import re
            detailed_answer = re.sub(r'[<>{}*#]', '', detailed_answer)
            
            # Limit for voice output
            if len(detailed_answer) > 200:
                sentences = detailed_answer.split('.')
                if len(sentences) >= 2:
                    detailed_answer = sentences[0] + '. ' + sentences[1] + '.'
                else:
                    detailed_answer = sentences[0] + '.'
            
            final_response = detailed_answer.strip()
            print(f"\n🎯 Final Voice Response: {final_response}")
        else:
            print("❌ Failed to get proper detailed answer")
    
    except Exception as e:
        print(f"❌ Error in response formatting: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run debug
    debug_voice_assistant_rag()
    
    # Test exact flow
    test_exact_voice_assistant_flow()