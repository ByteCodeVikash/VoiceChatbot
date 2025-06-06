# Enhanced Synonym Dictionary for Government Schemes Search

SYNONYMS = {
    # Farmer/Agriculture related
    "farmer": ["kisan", "किसान", "farmers", "krishak", "कृषक", "agriculture", "krishi", "कृषि", "farming", "खेती"],
    "agriculture": ["farming", "कृषि", "krishi", "खेती", "khet", "crop", "cultivation", "किसान", "farmer"],
    "farming": ["खेती", "agriculture", "कृषि", "cultivation", "crop", "farmer", "किसान"],
    "crop": ["फसल", "fasal", "produce", "harvest", "उत्पादन"],
    
    # Water/Irrigation
    "borewell": ["tubewell", "boring", "बोरवेल", "बोरिंग", "kuan", "कुआं", "water pump", "पानी पंप", "well", "tube well"],
    "water": ["जल", "pani", "पानी", "irrigation", "सिंचाई", "pump", "पम्प"],
    "irrigation": ["सिंचाई", "water", "जल", "pump", "borewell", "tubewell"],
    "pump": ["पम्प", "water pump", "irrigation", "सिंचाई"],
    
    # Specific Crops
    "coffee": ["कॉफी", "coffee bean", "कॉफी बीन", "plantation", "बागान", "arabica", "robusta"],
    "sugarcane": ["गन्ना", "ganna", "sugar", "चीनी"],
    "cotton": ["कपास", "kapas", "रुई"],
    "rice": ["चावल", "chawal", "धान", "dhan"],
    "wheat": ["गेहूं", "gehun"],
    
    # Fishing/Marine
    "fisherman": ["machhuara", "मछुआरा", "fisher", "मछली", "fishing", "मत्स्य", "matsya", "marine"],
    "fishing": ["मछली पकड़ना", "marine", "boat", "नाव", "fisherman", "मछुआरा"],
    "boat": ["नाव", "nav", "vessel", "fishing boat", "marine"],
    "marine": ["समुद्री", "sea", "ocean", "fishing", "boat"],
    
    # Women/Gender
    "women": ["महिला", "mahila", "female", "lady", "woman", "girl", "बेटी"],
    "woman": ["महिला", "mahila", "female", "lady", "women"],
    "female": ["महिला", "women", "woman", "lady"],
    "girl": ["लड़की", "ladki", "बेटी", "beti"],
    
    # Financial Terms
    "subsidy": ["sahayata", "सहायता", "madad", "मदद", "grant", "anudan", "अनुदान", "financial help", "वित्तीय सहायता"],
    "loan": ["ऋण", "rin", "credit", "कर्ज", "karj", "finance", "वित्त", "mudra"],
    "money": ["पैसा", "paisa", "रुपया", "rupaya", "cash", "नकद", "financial", "वित्तीय"],
    "grant": ["अनुदान", "anudan", "subsidy", "सहायता", "help", "मदद"],
    "insurance": ["बीमा", "bima", "coverage", "protection", "सुरक्षा"],
    
    # Business/Employment
    "business": ["व्यवसाय", "vyavasaya", "udyog", "उद्योग", "trade", "व्यापार", "vyapar"],
    "employment": ["रोजगार", "rojgar", "job", "नौकरी", "naukri", "work", "काम"],
    "entrepreneurship": ["उद्यमिता", "business", "व्यवसाय", "startup"],
    "self employment": ["स्वरोजगार", "swarojgar", "own business", "entrepreneurship"],
    
    # Training/Education
    "training": ["प्रशिक्षण", "prashikshan", "education", "शिक्षा", "skill", "कौशल", "course", "पाठ्यक्रम"],
    "education": ["शिक्षा", "shiksha", "training", "प्रशिक्षण", "learning", "सीखना"],
    "skill": ["कौशल", "kaushal", "training", "प्रशिक्षण", "ability", "योग्यता"],
    "course": ["पाठ्यक्रम", "training", "प्रशिक्षण", "class", "कक्षा"],
    "scholarship": ["छात्रवृत्ति", "chhatravritti", "education", "शिक्षा", "student aid"],
    
    # Poultry/Livestock
    "poultry": ["मुर्गी पालन", "murgi palan", "chicken", "मुर्गी", "bird", "पक्षी"],
    "livestock": ["पशुधन", "pashudan", "cattle", "गाय", "buffalo", "भैंस"],
    "dairy": ["डेयरी", "milk", "दूध", "cow", "गाय", "buffalo", "भैंस"],
    
    # States and Regions
    "gujarat": ["गुजरात", "guj", "ahmedabad", "अहमदाबाद", "gandhinagar", "गांधीनगर"],
    "andhra pradesh": ["आंध्र प्रदेश", "ap", "andhra", "hyderabad", "हैदराबाद"],
    "goa": ["गोवा", "panaji", "पणजी"],
    "karnataka": ["कर्नाटक", "bangalore", "बंगलोर", "mysore", "मैसूर"],
    "north eastern": ["उत्तर पूर्वी", "northeast", "ne", "seven sisters"],
    "kerala": ["केरल", "kochi", "कोच्चि", "thiruvananthapuram"],
    "tamil nadu": ["तमिल नाडु", "tn", "chennai", "चेन्नई"],
    "maharashtra": ["महाराष्ट्र", "mh", "mumbai", "मुंबई", "pune", "पुणे"],
    "uttar pradesh": ["उत्तर प्रदेश", "up", "lucknow", "लखनौ"],
    "rajasthan": ["राजस्थान", "jaipur", "जयपुर"],
    "punjab": ["पंजाब", "chandigarh", "चंडीगढ़"],
    "haryana": ["हरियाणा", "chandigarh", "चंडीगढ़"],
    
    # Government Terms
    "scheme": ["yojana", "योजना", "schemes", "yojanayen", "योजनाएं", "program", "programme", "कार्यक्रम"],
    "government": ["सरकार", "sarkar", "सरकारी", "sarkari", "govt", "राज्य", "rajya", "केंद्र", "kendra"],
    "ministry": ["मंत्रालय", "mantralaya", "department", "विभाग", "vibhag"],
    
    # Application Process
    "apply": ["आवेदन", "aavedan", "registration", "पंजीकरण", "panjikar", "form", "फॉर्म"],
    "application": ["आवेदन", "aavedan", "form", "फॉर्म", "registration"],
    "registration": ["पंजीकरण", "panjikar", "registration", "apply", "आवेदन"],
    "form": ["फॉर्म", "application", "आवेदन", "paper", "कागज"],
    
    # Documents
    "documents": ["दस्तावेज", "dastavej", "papers", "कागज", "kagaj", "certificates", "प्रमाणपत्र", "pramaan"],
    "certificate": ["प्रमाणपत्र", "pramaan", "documents", "दस्तावेज"],
    "id proof": ["पहचान प्रमाण", "identity", "आधार", "aadhar"],
    
    # Eligibility
    "eligibility": ["पात्रता", "patrta", "qualification", "योग्यता", "yogyata", "criteria", "मापदंड"],
    "eligible": ["पात्र", "patr", "qualified", "योग्य", "yogya"],
    "criteria": ["मापदंड", "eligibility", "पात्रता", "conditions"],
    
    # Common Questions Words
    "how": ["कैसे", "kaise", "किस तरह", "kis tarah"],
    "what": ["क्या", "kya", "कौन सा", "kaun sa"],
    "where": ["कहाँ", "kahan", "किस जगह", "kis jagah"],
    "when": ["कब", "kab", "कितने समय", "kitne samay"],
    "who": ["कौन", "kaun", "किसे", "kise"],
    "why": ["क्यों", "kyun", "किसलिए", "kisliye"],
    
    # Common Verbs
    "get": ["मिलना", "milna", "पाना", "pana", "प्राप्त", "prapt"],
    "receive": ["प्राप्त करना", "prapt karna", "मिलना", "milna"],
    "need": ["चाहिए", "chahiye", "जरूरत", "jarurat", "आवश्यकता", "avashyakta"],
    "want": ["चाहना", "chahna", "चाहिए", "chahiye"],
    "help": ["मदद", "madad", "सहायता", "sahayata", "सहयोग", "sahyog"],
    
    # Benefits
    "benefit": ["लाभ", "labh", "फायदा", "fayda", "advantage", "सुविधा", "suvidha"],
    "advantage": ["फायदा", "fayda", "लाभ", "labh", "benefit"],
    "profit": ["मुनाफा", "munafa", "लाभ", "labh"],
    
    # Amounts/Financial
    "free": ["मुफ्त", "muft", "निःशुल्क", "nishulk", "bedagat", "बेदाग"],
    "cost": ["लागत", "lagat", "कीमत", "kimat", "खर्च", "kharch"],
    "price": ["कीमत", "kimat", "दाम", "daam", "मूल्य", "mulya"],
    "amount": ["राशि", "rashi", "मात्रा", "matra", "रकम", "rakam"],
    
    # Time related
    "time": ["समय", "samay", "वक्त", "waqt"],
    "duration": ["अवधि", "avadhi", "समयावधि", "samayavadhi"],
    "period": ["काल", "kaal", "अवधि", "avadhi"],
    
    # Disaster/Emergency
    "disaster": ["आपदा", "apda", "प्राकृतिक आपदा", "natural disaster"],
    "calamity": ["आपदा", "apda", "विपदा", "vipda"],
    "storm": ["तूफान", "toofan", "आंधी", "andhi"],
    "flood": ["बाढ़", "badh", "जल प्रलय", "jal pralay"],
    
    # Special Terms
    "damaged": ["क्षतिग्रस्त", "kshatigrast", "टूटा", "toota", "खराब", "kharab"],
    "relief": ["राहत", "rahat", "सहायता", "sahayata", "मदद", "madad"],
    "compensation": ["मुआवजा", "muaavja", "भरपाई", "bharpaai"]
}

def get_synonyms(word):
    """Get all synonyms for a given word"""
    word_lower = word.lower().strip()
    
    # Direct lookup
    for key, values in SYNONYMS.items():
        if word_lower == key or word_lower in [v.lower() for v in values]:
            return [key] + values
    
    # Partial matching for compound words
    for key, values in SYNONYMS.items():
        if word_lower in key or key in word_lower:
            return [key] + values
        for value in values:
            if word_lower in value.lower() or value.lower() in word_lower:
                return [key] + values
    
    return [word]

def expand_query(query):
    """Expand query with synonyms and related terms"""
    if not query:
        return ""
    
    words = query.split()
    expanded_words = []
    
    for word in words:
        # Clean word
        clean_word = word.strip('।.,!?"""''()[]{}')
        
        # Get synonyms
        synonyms = get_synonyms(clean_word)
        
        # Add original word and key synonyms (limit to avoid too long queries)
        expanded_words.append(clean_word)
        if len(synonyms) > 1:
            # Add up to 3 most relevant synonyms
            expanded_words.extend(synonyms[1:4])
    
    return " ".join(expanded_words)

def get_occupation_keywords(occupation):
    """Get specific keywords for occupation-based search"""
    occupation_map = {
        "farmer": ["farmer", "किसान", "agriculture", "farming", "crop", "कृषि", "खेती"],
        "fisherman": ["fisherman", "मछुआरा", "fishing", "marine", "boat", "मत्स्य"],
        "women": ["women", "महिला", "female", "woman", "lady"],
        "business": ["business", "व्यवसाय", "entrepreneur", "mudra", "loan"],
        "student": ["student", "विद्यार्थी", "education", "scholarship", "छात्रवृत्ति"]
    }
    
    return occupation_map.get(occupation, [])

def get_location_keywords(location):
    """Get specific keywords for location-based search"""
    if not location:
        return []
    
    location_lower = location.lower()
    
    # Find matching location and return its keywords
    for key, values in SYNONYMS.items():
        if location_lower == key or location_lower in [v.lower() for v in values]:
            if any(state in key for state in ['gujarat', 'andhra', 'goa', 'karnataka', 'kerala']):
                return [key] + values
    
    return [location]

def enhance_search_query(query, occupation=None, location=None):
    """Enhanced query building with context"""
    enhanced_parts = [query]
    
    # Add occupation context
    if occupation:
        occ_keywords = get_occupation_keywords(occupation)
        enhanced_parts.extend(occ_keywords[:3])  # Add top 3 keywords
    
    # Add location context
    if location:
        loc_keywords = get_location_keywords(location)
        enhanced_parts.extend(loc_keywords[:2])  # Add top 2 keywords
    
    # Expand with synonyms
    expanded_query = expand_query(" ".join(enhanced_parts))
    
    return expanded_query