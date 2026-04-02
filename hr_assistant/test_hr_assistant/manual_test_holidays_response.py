"""Test script to see the raw LLM response for public holidays."""

import logging
from app.services.hr_policy_service import get_ai_service

# Enable debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_holidays_response():
    """Test what the LLM responds for public holidays."""
    print("=== Testing Public Holidays Response ===")
    
    try:
        # Get AI service
        ai_service = get_ai_service()
        
        # Ask about public holidays
        print("\n1. Asking: What are the public holidays?")
        response1 = ai_service.generate_response(
            question="What are the public holidays?",
            conversation_history=None
        )
        print("\nRaw Response 1:")
        print("=" * 50)
        print(response1)
        print("=" * 50)
        
        # Ask to format as table
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
        print("\nRaw Response 2 (Table):")
        print("=" * 50)
        print(response2)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_holidays_response()
