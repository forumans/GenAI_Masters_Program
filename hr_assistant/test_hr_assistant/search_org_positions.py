"""Search for specific org positions."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.hr_policy_service import get_ai_service

def search_org_positions():
    """Search for specific org positions."""
    print("=== Searching Org Positions ===")
    
    ai_service = get_ai_service()
    
    # Search for different parts of the org
    searches = [
        "Board of Directors CEO CFO COO",
        "HR Director Finance Department",
        "Division Director reporting",
        "organizational reporting relationships"
    ]
    
    for search in searches:
        print(f"\n--- Searching for: {search} ---")
        context_docs = ai_service.retriever.invoke(search)
        
        for i, doc in enumerate(context_docs[:2]):  # Top 2 docs
            if any(term in doc.page_content for term in ["Board", "CEO", "CFO", "Director"]):
                print(f"Doc {i+1}: {doc.page_content[:300]}...")

if __name__ == "__main__":
    search_org_positions()
