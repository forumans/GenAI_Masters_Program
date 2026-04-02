"""Test the new interactive tree format."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.hr_policy_service import get_ai_service
import json

def test_interactive_tree():
    """Test the new interactive JSON tree format."""
    print("=== Testing Interactive Tree Format ===")
    
    ai_service = get_ai_service()
    
    question = "What is the org structure?"
    response = ai_service.generate_response(question)
    
    try:
        parsed = json.loads(response)
        
        if parsed.get('type') == 'tree':
            print("✓ Tree response detected")
            data = parsed.get('data')
            
            if isinstance(data, dict) and 'name' in data:
                print("✓ New JSON tree format detected")
                print(f"Root: {data['name']}")
                
                def print_tree(node, level=0):
                    indent = "  " * level
                    print(f"{indent}- {node['name']}")
                    if 'children' in node:
                        for child in node['children']:
                            print_tree(child, level + 1)
                
                print("\nTree Structure:")
                print_tree(data)
            else:
                print("✗ Old string format detected")
                print(f"Data type: {type(data)}")
                
        else:
            print(f"✗ Not a tree response: {parsed.get('type')}")
            
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON: {e}")
        print(f"Response: {response[:200]}...")

if __name__ == "__main__":
    test_interactive_tree()
