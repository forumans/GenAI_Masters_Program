"""Test tree response with actual line breaks."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.hr_policy_service import get_ai_service

def test_tree_response():
    """Test tree response with line breaks."""
    print("=== Testing Tree Response ===")
    
    ai_service = get_ai_service()
    
    # Test with explicit tree request
    question = "Show me the org chart in tree format"
    response = ai_service.generate_response(question)
    
    print(f"Question: {question}")
    print(f"\nResponse:\n{response}")
    print("\n" + "="*50)
    print("Response with \\n visible:")
    print(response.replace("\n", "\\n"))
    print("\n" + "="*50)
    print("Raw response repr:")
    print(repr(response))

if __name__ == "__main__":
    test_tree_response()
