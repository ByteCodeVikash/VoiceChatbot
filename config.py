CONFIG = {
    "schemes_csv_path": "Government_schemes_final_english.csv",
    "audio_timeout": 5,
    "confidence_threshold": 0.5,
    "voice_rate": 0.9,
    "voice_volume": 1.0,
    "tts_model": "tts_models/multilingual/multi-dataset/xtts_v2",
    "speaker_en": "speakers/en_male.wav",  # Path to English speaker sample
    "speaker_hi": "speakers/hi_female.wav",  # Path to Hindi speaker sample
    "whisper_model_size": "small",
    "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
    "fasttext_model": "lid.176.bin",
    "indictrans_model": "indictrans2",
    "rasa_model_path": "models/rasa/nlu",
    "csv_hash_algorithm": "sha256"
}

# Keep the PHRASES dictionary as is

PHRASES = {
    "welcome": {
        "english": "Welcome to the Government Schemes Helpdesk. How can I assist you today?",
        "hindi": "सरकारी योजनाओं के हेल्पडेस्क में आपका स्वागत है। मैं आपकी कैसे सहायता कर सकता हूँ?",
        "hinglish": "Government Schemes Helpdesk mein aapka swagat hai. Main aapki kaise help kar sakta hoon?"
    },
    "select_language": {
        "english": "Please select your preferred language. Say English, Hindi, or Hinglish.",
        "hindi": "कृपया अपनी पसंदीदा भाषा चुनें। इंग्लिश, हिंदी, या हिंग्लिश कहें।",
        "hinglish": "Please apni preferred language select karein. English, Hindi, ya Hinglish kahein."
    },
    "language_selected": {
        "english": "You have selected English. Let's continue.",
        "hindi": "आपने हिंदी चुनी है। आगे बढ़ते हैं।",
        "hinglish": "Aapne Hinglish select kiya hai. Chaliye continue karte hain."
    },
    "language_not_understood": {
        "english": "I couldn't understand your language choice. Using English as default.",
        "hindi": "मैं आपकी भाषा पसंद को नहीं समझ सका। डिफ़ॉल्ट रूप से इंग्लिश का उपयोग कर रहा हूँ।",
        "hinglish": "Main aapki language choice ko samajh nahi saka. Default taur par English use kar raha hoon."
    },
    "ask_name": {
        "english": "May I have your name, please?",
        "hindi": "क्या मैं आपका नाम जान सकता हूँ?",
        "hinglish": "Kya main aapka naam jaan sakta hoon?"
    },
    "thank_you": {
        "english": "Thank you, {}.",
        "hindi": "धन्यवाद, {}।",
        "hinglish": "Thank you, {}."
    },
    "ask_query": {
        "english": "How can I assist you with government schemes today?",
        "hindi": "मैं आज सरकारी योजनाओं के बारे में आपकी कैसे सहायता कर सकता हूँ?",
        "hinglish": "Aaj main government schemes ke baare mein aapki kaise help kar sakta hoon?"
    },
    "ask_occupation": {
        "english": "Can you tell me your occupation or location to suggest relevant schemes?",
        "hindi": "क्या आप अपना व्यवसाय या स्थान बता सकते हैं ताकि मैं आपके लिए उपयुक्त योजनाएं सुझा सकूँ?",
        "hinglish": "Kya aap apna occupation ya location bata sakte hain taaki main relevant schemes suggest kar sakun?"
    },
    "closing": {
        "english": "Thank you for contacting us, {}. Have a nice day!",
        "hindi": "हमसे संपर्क करने के लिए धन्यवाद, {}। आपका दिन शुभ हो!",
        "hinglish": "Humse contact karne ke liye thank you, {}. Aapka din shubh ho!"
    },
    "didnt_catch": {
        "english": "I didn't catch that. Please try again.",
        "hindi": "मैं वह नहीं समझ पाया। कृपया फिर से प्रयास करें।",
        "hinglish": "Main woh nahi samajh paya. Please dobara try karein."
    },
    "anything_else": {
        "english": "Is there anything else I can help you with?",
        "hindi": "क्या मैं आपकी और कोई मदद कर सकता हूँ?",
        "hinglish": "Kya main aapki aur koi madad kar sakta hoon?"
    },
    "no_schemes": {
        "english": "I couldn't find any relevant schemes based on your query. Could you please provide more details about what you're looking for?",
        "hindi": "मुझे आपकी क्वेरी के आधार पर कोई प्रासंगिक योजना नहीं मिली। क्या आप कृपया बता सकते हैं कि आप किस प्रकार की योजना के बारे में जानना चाहते हैं?",
        "hinglish": "Mujhe aapki query ke basis par koi relevant scheme nahi mili. Kya aap please bata sakte hain ki aap kis type ki scheme ke baare mein janna chahte hain?"
    },
    "schemes_intro": {
        "english": "Here are the most relevant government schemes based on your query:",
        "hindi": "आपकी क्वेरी के आधार पर यहां सबसे प्रासंगिक सरकारी योजनाएं हैं:",
        "hinglish": "Aapki query ke basis par yahan sabse relevant government schemes hain:"
    },
    "initializing": {
        "english": "Initializing government schemes voice assistant...",
        "hindi": "सरकारी योजना वॉइस असिस्टेंट शुरू हो रहा है...",
        "hinglish": "Government scheme voice assistant initialize ho raha hai..."
    },
    "error_tts": {
        "english": "I'm having trouble speaking right now. Please check your audio setup.",
        "hindi": "मुझे बोलने में परेशानी हो रही है। कृपया अपना ऑडियो सेटअप जांचें।",
        "hinglish": "Mujhe bolne mein problem ho rahi hai. Please apna audio setup check karein."
    },
    "error_recognizer": {
        "english": "I'm having trouble hearing you. Please check your microphone.",
        "hindi": "मुझे आपको सुनने में परेशानी हो रही है। कृपया अपना माइक्रोफोन जांचें।",
        "hinglish": "Mujhe aapko sunne mein problem ho rahi hai. Please apna microphone check karein."
    },
    "good_morning": {
        "english": "Good morning, {}!",
        "hindi": "सुप्रभात, {}!",
        "hinglish": "Good morning, {}!"
    },
    "good_afternoon": {
        "english": "Good afternoon, {}!",
        "hindi": "शुभ दोपहर, {}!",
        "hinglish": "Good afternoon, {}!"
    },
    "good_evening": {
        "english": "Good evening, {}!",
        "hindi": "शुभ संध्या, {}!",
        "hinglish": "Good evening, {}!"
    },
    "loading_components": {
        "english": "Loading necessary components, please wait...",
        "hindi": "आवश्यक कंपोनेंट्स लोड हो रहे हैं, कृपया प्रतीक्षा करें...",
        "hinglish": "Necessary components load ho rahe hain, please wait karein..."
    },
    "component_ready": {
        "english": "Ready for your commands!",
        "hindi": "आपके निर्देशों के लिए तैयार!",
        "hinglish": "Aapke commands ke liye ready!"
    }
}