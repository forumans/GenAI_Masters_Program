"""Test tree response to verify line breaks."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.hr_policy_service import get_ai_service

def test_tree_response():
    """Test tree response to verify line breaks."""
    print("=== Testing Tree Response ===")
    
    ai_service = get_ai_service()
    
    question = "What is the org structure?"
    response = ai_service.generate_response(question)
    
    print(f"Question: {question}")
    print(f"\nResponse as displayed:\n{response}")
    print("\n" + "="*50)
    print("Response with visible line breaks (\\n):")
    print(response.replace("\n", "\\n"))
    print("\n" + "="*50)
    print("Raw repr of response:")
    print(repr(response))
    
    # Check if it has line breaks
    if "\n" in response:
        print("\n✓ Response contains line breaks")
    else:
        print("\n✗ Response does NOT contain line breaks")
    
    # Count lines
    lines = response.split("\n")
    print(f"\nNumber of lines: {len(lines)}")

if __name__ == "__main__":
    test_tree_response()
