"""Check what prompt is being sent to LLM."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.hr_policy_service import get_ai_service

def check_prompt():
    """Check what prompt is being sent to LLM."""
    print("=== Checking Prompt ===")
    
    ai_service = get_ai_service()
    
    question = "Show me the org chart in tree format"
    
    # Get the retriever
    context_docs = ai_service.retriever.invoke(question)
    context = "\n\n---\n\n".join([doc.page_content for doc in context_docs])
    
    # Format the prompt
    chain_input = {
        "question": question,
        "history": "",
        "context": context,
        "employee_context": ""
    }
    
    formatted_prompt = ai_service.rag_prompt.format(**chain_input)
    
    # Check if tree instructions are in the prompt
    if "TREE/DIAGRAM OUTPUT MODE" in formatted_prompt:
        print("✓ Tree instructions found in prompt")
        # Find and print the tree section
        start = formatted_prompt.find("TREE/DIAGRAM OUTPUT MODE:")
        end = formatted_prompt.find("NON-TABLE OUTPUT MODE:", start)
        if end != -1:
            tree_section = formatted_prompt[start:end]
            print("\n--- Tree Section ---")
            print(tree_section[:1000])  # First 1000 chars
    else:
        print("✗ Tree instructions NOT found in prompt")
    
    # Check if org structure is in the prompt
    if "Board of Directors" in formatted_prompt and "└── CEO" in formatted_prompt:
        print("\n✓ Org structure example found in prompt")
    else:
        print("\n✗ Org structure example NOT found in prompt")

if __name__ == "__main__":
    check_prompt()
