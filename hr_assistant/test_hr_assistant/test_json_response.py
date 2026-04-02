"""Test the new JSON response format."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.hr_policy_service import get_ai_service
import json

def test_json_response():
    """Test the new structured JSON response format."""
    print("=== Testing JSON Response Format ===")
    
    ai_service = get_ai_service()
    
    questions = [
        "What is the org structure?",
        "List all holidays",
        "How many employees are there?",
        "What is the vacation policy?"
    ]
    
    for question in questions:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print('='*60)
        
        response = ai_service.generate_response(question)
        
        try:
            parsed = json.loads(response)
            print(f"✓ Valid JSON response")
            print(f"Type: {parsed.get('type', 'unknown')}")
            print(f"Has data: {'data' in parsed}")
            if 'meta' in parsed:
                print(f"Meta: {parsed['meta']}")
            
            # Show a preview of the data
            if isinstance(parsed.get('data'), str):
                preview = parsed['data'][:100] + "..." if len(parsed['data']) > 100 else parsed['data']
                print(f"Data preview: {preview}")
            else:
                print(f"Data type: {type(parsed.get('data')).__name__}")
                
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON: {e}")
            print(f"Raw response: {response[:200]}...")

if __name__ == "__main__":
    test_json_response()
