"""Get the full org chart content."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.hr_policy_service import get_ai_service

def get_full_org_chart():
    """Get the full org chart content."""
    print("=== Getting Full Org Chart ===")
    
    ai_service = get_ai_service()
    
    # Search for org chart specifically
    question = "Tri-County Community Action Programs Inc. Organizational Chart"
    
    # Retrieve context
    context_docs = ai_service.retriever.invoke(question)
    print(f"Retrieved {len(context_docs)} documents:")
    
    for i, doc in enumerate(context_docs):
        if "Organizational Chart" in doc.page_content:
            print(f"\n--- Document {i+1} (Full Content) ---")
            print(doc.page_content)
            break

if __name__ == "__main__":
    get_full_org_chart()
