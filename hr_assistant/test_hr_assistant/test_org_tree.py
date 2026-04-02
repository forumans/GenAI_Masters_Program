"""Test org structure tree response."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.hr_policy_service import get_ai_service

def test_org_tree():
    """Test the org structure tree response."""
    print("=== Testing Org Structure Tree ===")
    
    ai_service = get_ai_service()
    
    question = "What is the org structure?"
    response = ai_service.generate_response(question)
    
    print(f"Question: {question}")
    print(f"\nResponse:\n{response}")
    print("\n" + "="*50)
    print("Response with visible line breaks:")
    print(repr(response))

if __name__ == "__main__":
    test_org_tree()
