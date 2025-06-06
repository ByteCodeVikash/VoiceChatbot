# config.py - Enhanced with Groq API
CONFIG = {
    "schemes_csv_path": "Government_schemes_final_english.csv",
    "audio_timeout": 6,
    "confidence_threshold": 0.3,
    "voice_rate": 0.9,
    "voice_volume": 1.0,
    "tts_model": "xtts_v2",
    "whisper_model_size": "small",
    "ollama_model": "phi3:mini",
    "synonym_dict_path": "synonym_dict.py",
    "sqlite_db_path": "schemes.db",
    "cache_dir": "assets/cache/",
    "sample_rate": 44100,
    "csv_hash_algorithm": "sha256",
    # Groq API Configuration
    "GROQ_API_KEY": "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",
    "groq_model": "deepseek-r1-distill-llama-70b",
    "groq_temperature": 0.1,
    "rag_chunk_size": 1000,
    "rag_chunk_overlap": 100,
    "max_schemes_per_response": 3,
    # Enable RAG
    "use_rag": True,
    "rag_enabled": True
}

PHRASES = {
    "welcome": {
        "english": "Welcome to Government Schemes Helpdesk. How can I help you?",
        "hindi": "सरकारी योजनाओं के हेल्पडेस्क में आपका स्वागत है। मैं आपकी कैसे सहायता कर सकता हूँ?",
        "hinglish": "Government Schemes Helpdesk mein aapka swagat hai। Main aapki kaise help kar sakta hoon?"
    },
    "select_language": {
        "english": "Please select your language: English, Hindi, or Hinglish।",
        "hindi": "कृपया अपनी भाषा चुनें: इंग्लिश, हिंदी, या हिंग्लिश।",
        "hinglish": "Please apni language select karein: English, Hindi, ya Hinglish।"
    },
    "language_selected": {
        "english": "You selected English। Let's continue।",
        "hindi": "आपने हिंदी चुनी है। आगे बढ़ते हैं।",
        "hinglish": "Aapne Hinglish select kiya है। Chaliye continue karte hain।"
    },
    "ask_name": {
        "english": "What's your name?",
        "hindi": "आपका नाम क्या है?",
        "hinglish": "Aapka naam kya hai?"
    },
    "thank_you": {
        "english": "Thank you, {}।",
        "hindi": "धन्यवाद, {}।",
        "hinglish": "Thank you, {}।"
    },
    "ask_query": {
        "english": "How can I help you with government schemes?",
        "hindi": "मैं सरकारी योजनाओं के बारे में आपकी कैसे सहायता कर सकता हूँ?",
        "hinglish": "Main government schemes ke baare mein aapki kaise help kar sakta hoon?"
    },
    "ask_occupation": {
        "english": "Tell me your occupation or location for better scheme suggestions।",
        "hindi": "अपना व्यवसाय या स्थान बताएं ताकि मैं बेहतर योजनाएं सुझा सकूं।",
        "hinglish": "Apna occupation ya location batayiye better schemes suggest karne ke liye।"
    },
    "closing": {
        "english": "Thank you for contacting us, {}। Have a nice day!",
        "hindi": "हमसे संपर्क करने के लिए धन्यवाद, {}। आपका दिन शुभ हो!",
        "hinglish": "Humse contact karne ke liye thank you, {}। Aapka din shubh ho!"
    },
    "didnt_catch": {
        "english": "I didn't catch that। Please try again।",
        "hindi": "मैं समझ नहीं पाया। कृपया फिर से कहें।",
        "hinglish": "Main samajh nahi paya। Please dobara boliye।"
    },
    "anything_else": {
        "english": "Anything else I can help you with?",
        "hindi": "क्या मैं आपकी और कोई मदद कर सकता हूँ?",
        "hinglish": "Kya main aapki aur koi madad kar sakta hoon?"
    },
    "no_schemes": {
        "english": "I couldn't find relevant schemes। Please provide more details।",
        "hindi": "मुझे उपयुक्त योजनाएं नहीं मिलीं। कृपया अधिक जानकारी दें।",
        "hinglish": "Mujhe suitable schemes nahi mili। Please aur details dijiye।"
    },
    "schemes_intro": {
        "english": "Here are relevant government schemes:",
        "hindi": "यहां उपयुक्त सरकारी योजनाएं हैं:",
        "hinglish": "Yahan suitable government schemes hain:"
    },
    "rag_processing": {
        "english": "Processing your query with AI...",
        "hindi": "आपकी क्वेरी को AI से प्रोसेस कर रहे हैं...",
        "hinglish": "Aapki query ko AI se process kar rahe hain..."
    },
    "rag_success": {
        "english": "Found relevant schemes for you!",
        "hindi": "आपके लिए संबंधित योजनाएं मिलीं!",
        "hinglish": "Aapke liye relevant schemes mili!"
    }
}