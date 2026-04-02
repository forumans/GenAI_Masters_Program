"""Check if tree request is being detected."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

def check_tree_detection():
    """Check if tree request is being detected."""
    print("=== Checking Tree Detection ===")
    
    questions = [
        "What is the org structure?",
        "Show me the org chart in tree format",
        "organizational structure",
        "org chart",
        "hierarchy"
    ]
    
    table_keywords = ["table", "put in a table", "show as a table", "display as table", "format as table", "tree", "hierarchy", "org chart", "tree format", "tree diagram", "organizational structure", "org structure", "reporting structure", "organization chart"]
    
    for question in questions:
        is_table_request = any(keyword in question.lower() for keyword in table_keywords)
        print(f"Question: '{question}'")
        print(f"  Detected as tree request: {is_table_request}")
        print()

if __name__ == "__main__":
    check_tree_detection()
