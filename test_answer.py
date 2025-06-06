# test_answer.py - Direct Test from fixed_perfect_rag approach
from enhanced_rag_database import answer_schemes_question

def test_single_question():
    """Test single question like the working example"""
    question = "What schemes are available for women?"
    print(f"Question: {question}")
    print("="*50)
    
    answer = answer_schemes_question(question)
    print(f"Answer: {answer}")

def test_krushi_mahotsav():
    """Test the specific Krushi Mahotsav query"""
    question = "how can I get seeds and fertilizers for free during Krushi Mahotsav in Gujarat"
    print(f"\nQuestion: {question}")
    print("="*50)
    
    answer = answer_schemes_question(question)
    print(f"Answer: {answer}")

def test_agriculture_schemes():
    """Test agriculture schemes"""
    question = "Show me agriculture schemes for farmers"
    print(f"\nQuestion: {question}")
    print("="*50)
    
    answer = answer_schemes_question(question)
    print(f"Answer: {answer}")

if __name__ == "__main__":
    print("🧪 Testing Direct CSV Data Fetch")
    print("=" * 60)
    
    # Test the questions
    test_single_question()
    test_krushi_mahotsav()
    test_agriculture_schemes()