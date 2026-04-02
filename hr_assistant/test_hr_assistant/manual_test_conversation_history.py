"""Test script to verify conversation history is working correctly."""

import logging
from app.services.hr_policy_service import get_ai_service

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_conversation_history():
    """Test conversation history with reformatting request."""
    print("=== Testing Conversation History ===")
    
    try:
        # Get AI service
        ai_service = get_ai_service()
        
        # Simulate first question about holidays
        print("\n1. Asking: What are the public holidays?")
        response1 = ai_service.generate_response(
            question="What are the public holidays?",
            conversation_history=None
        )
        print(f"Response 1: {response1[:200]}...")
        
        # Simulate follow-up question to reformat
        print("\n2. Asking: Display those in a tabular format")
        
        # Create conversation history
        history = [
            {"role": "user", "content": "What are the public holidays?"},
            {"role": "assistant", "content": response1}
        ]
        
        response2 = ai_service.generate_response(
            question="Display those in a tabular format",
            conversation_history=history
        )
        print(f"Response 2: {response2}")
        
        # Check if response contains a table
        if "|" in response2 and "table" in response2.lower():
            print("\n✅ SUCCESS: Response contains a table!")
        else:
            print("\n❌ FAILED: Response does not contain a table")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conversation_history()
