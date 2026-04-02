"""Test org structure retrieval with the actual AI service."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.ai_service import AIService
from app.services.vector_store import VectorStoreService
from app.config import settings

def test_org_retrieval():
    """Test how the AI service retrieves org structure."""
    print("=== Testing Org Structure Retrieval ===")
    
    try:
        # Initialize vector store
        vector_store = VectorStoreService(
            persist_directory="chroma_data",
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Load PDF
        pdf_path = "../hr_policies/hr_policies.pdf"
        print(f"Loading PDF from {pdf_path}...")
        vector_store.load_pdf(pdf_path)
        
        # Initialize AI service
        ai_service = AIService(
            openai_api_key=settings.OPENAI_API_KEY,
            vector_store=vector_store
        )
        
        # Test different queries
        queries = [
            "What is the organizational structure?",
            "Show me the organizational chart",
            "What is shown in the organizational chart on page 4?",
            "Tri-County Community Action Programs Inc. organizational chart",
            "Who are the executives in the organization?"
        ]
        
        for query in queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print('='*60)
            
            response = ai_service.generate_response(query)
            print(f"\nResponse:\n{response}")
            print("\n" + "-"*60)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_org_retrieval()
