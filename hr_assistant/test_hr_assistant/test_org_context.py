"""Test what context is retrieved for org structure."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.hr_policy_service import get_ai_service

def test_org_context():
    """Test what context is retrieved for org structure."""
    print("=== Testing Org Structure Context ===")
    
    ai_service = get_ai_service()
    
    # Get the retriever
    question = "What is the org structure?"
    
    # Retrieve context
    context_docs = ai_service.retriever.invoke(question)
    print(f"Retrieved {len(context_docs)} documents:")
    
    for i, doc in enumerate(context_docs):
        print(f"\n--- Document {i+1} ---")
        print(f"Content: {doc.page_content[:500]}...")
        if 'metadata' in doc.metadata:
            print(f"Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"Page: {doc.metadata.get('page', 'Unknown')}")

if __name__ == "__main__":
    test_org_context()
