"""Check what organizational data is in ChromaDB."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.vector_store import VectorStoreService
from app.config import settings

def check_org_data():
    """Check what org data exists in the vector store."""
    print("=== Checking Organizational Data in ChromaDB ===")
    
    try:
        # Get vector store with proper initialization
        vector_store = VectorStoreService(
            persist_directory="chroma_data",
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Load the PDF to initialize the vector store
        pdf_path = "../hr_policies/hr_policies.pdf"
        if os.path.exists(pdf_path):
            print(f"Loading PDF from {pdf_path}...")
            vector_store.load_pdf(pdf_path)
        else:
            print(f"PDF not found at {pdf_path}")
            return
        
        # Search for org-related terms
        search_terms = [
            "organizational structure",
            "org chart",
            "Tri-County Community Action Programs",
            "Board of Directors",
            "CEO",
            "CFO",
            "COO"
        ]
        
        for term in search_terms:
            print(f"\nSearching for: '{term}'")
            print("-" * 40)
            results = vector_store.vector_store.similarity_search(
                term,
                k=3
            )
            
            if results:
                for i, doc in enumerate(results):
                    print(f"\nDocument {i+1}:")
                    print(f"Content: {doc.page_content[:300]}...")
                    if hasattr(doc, 'metadata') and doc.metadata:
                        print(f"Metadata: {doc.metadata}")
            else:
                print("No results found")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_org_data()
