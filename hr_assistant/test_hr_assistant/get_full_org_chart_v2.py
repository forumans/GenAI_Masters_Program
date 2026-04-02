"""Get the complete org chart with larger chunks."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.hr_policy_service import get_ai_service

def get_full_org_chart_v2():
    """Get the complete org chart with larger chunks."""
    print("=== Getting Full Org Chart v2 ===")
    
    ai_service = get_ai_service()
    
    # Get the retriever and check its chunk size
    print(f"Retriever type: {type(ai_service.retriever)}")
    
    # Try to get more context
    question = "Tri-County Community Action Programs Inc. Organizational Chart Board of Directors CEO CFO COO HR Director Division Directors"
    
    context_docs = ai_service.retriever.invoke(question)
    print(f"\nRetrieved {len(context_docs)} documents for extended query")
    
    # Look for the org chart document
    for i, doc in enumerate(context_docs):
        if "Organizational Chart" in doc.page_content and "Board of Directors" in doc.page_content:
            print(f"\n--- Org Chart Document {i+1} (Full Content) ---")
            print(doc.page_content)
            print(f"\nContent length: {len(doc.page_content)} characters")
            break

if __name__ == "__main__":
    get_full_org_chart_v2()
