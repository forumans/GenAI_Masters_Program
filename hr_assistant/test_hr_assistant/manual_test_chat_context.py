"""Test script to verify chat context retrieval and response quality."""

import logging
from app.services.hr_policy_service import get_ai_service
from app.config import settings

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_context_retrieval():
    """Test if context is being retrieved properly."""
    print("=== Testing Context Retrieval ===")
    
    try:
        # Get AI service (this loads the PDF)
        ai_service = get_ai_service()
        
        # Access the vector store through the AI service
        vector_store = ai_service.vector_store
        
        # Check if vector store has documents
        doc_count = vector_store.count()
        print(f"Vector store document count: {doc_count}")
        
        if doc_count == 0:
            print("❌ ERROR: No documents in vector store! PDF was not loaded.")
            return False
        
        # Test direct query to vector store
        print("\n=== Testing Vector Store Query ===")
        test_questions = [
            "What is the annual leave policy?",
            "How many sick days am I entitled to?",
            "What is the process for claiming expenses?",
            "What is the probation period?"
        ]
        
        for question in test_questions:
            print(f"\nQuestion: {question}")
            chunks = vector_store.query(question, n_results=3)
            if chunks:
                print(f"✓ Found {len(chunks)} relevant chunks")
                print(f"First chunk preview: {chunks[0][:300]}...")
            else:
                print("❌ No chunks found")
        
        # Test AI service response
        print("\n=== Testing AI Service Response ===")
        question = "What is the annual leave policy?"
        response = ai_service.generate_response(question)
        print(f"\nQuestion: {question}")
        print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_context_retrieval()
