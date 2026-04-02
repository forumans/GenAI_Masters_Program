"""Debug what context is retrieved for org structure queries."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.hr_policy_service import get_ai_service

def debug_org_context():
    """Debug org structure context retrieval."""
    print("=== Debugging Org Structure Context ===")
    
    ai_service = get_ai_service()
    
    # Try different queries
    queries = [
        "organizational structure",
        "org structure",
        "org chart",
        "Board of Directors CEO CFO",
        "Tri-County Community Action Programs Inc. Organizational Chart"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        context_docs = ai_service.retriever.invoke(query)
        print(f"Retrieved {len(context_docs)} documents")
        
        for i, doc in enumerate(context_docs):
            print(f"\n--- Document {i+1} ---")
            content = doc.page_content
            if len(content) > 500:
                content = content[:500] + "..."
            print(content)
            
            # Check for org keywords
            if any(keyword in doc.page_content.lower() for keyword in ['board', 'ceo', 'cfo', 'director', 'reporting']):
                print(">>> Contains org keywords!")

if __name__ == "__main__":
    debug_org_context()
