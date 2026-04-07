"""Test the leave query to see what response the AI gives."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.services.hr_policy_service import get_ai_service
from app.database import get_db
import json

def test_leave_query():
    """Test the query about employees on leave."""
    print("=== Testing Leave Query ===")
    
    ai_service = get_ai_service()
    
    # Get a database session
    db = next(get_db())
    
    try:
        question = "Can you show me the employees that are on leave?"
        response = ai_service.generate_response(question, db=db)
        
        try:
            parsed = json.loads(response)
            
            print(f"Response Type: {parsed.get('type')}")
            print(f"Response Title: {parsed.get('meta', {}).get('title', 'No title')}")
            print(f"Response Data:")
            
            if parsed.get('type') == 'table':
                data = parsed.get('data', {})
                print(f"  Columns: {data.get('columns', [])}")
                print(f"  Rows: {len(data.get('rows', []))}")
                for i, row in enumerate(data.get('rows', [])[:5]):  # Show first 5 rows
                    print(f"    Row {i+1}: {row}")
            elif parsed.get('type') == 'text':
                print(f"  {parsed.get('data', '')[:200]}...")
            else:
                print(f"  {json.dumps(parsed.get('data'), indent=2)}")
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Raw response: {response[:500]}...")
    finally:
        db.close()

if __name__ == "__main__":
    test_leave_query()
