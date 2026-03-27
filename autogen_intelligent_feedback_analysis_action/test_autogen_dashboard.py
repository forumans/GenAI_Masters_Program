#!/usr/bin/env python3
"""
Test script for AutoGen Streamlit Dashboard
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_autogen_import():
    """Test if AutoGen system can be imported"""
    try:
        from orchestration.autogen_manager import AutoGenFeedbackAnalysisSystem
        print("✅ AutoGenFeedbackAnalysisSystem imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import AutoGenFeedbackAnalysisSystem: {e}")
        return False

def test_dashboard_import():
    """Test if dashboard can be imported"""
    try:
        import streamlit as st
        from ui.dashboard import dashboard_page
        print("✅ Dashboard imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import dashboard: {e}")
        return False

def main():
    """Main test function"""
    print("🤖 Testing AutoGen Dashboard Setup")
    print("=" * 50)
    
    # Test imports
    import_success = test_autogen_import()
    dashboard_success = test_dashboard_import()
    
    if import_success and dashboard_success:
        print("\n✅ All tests passed!")
        print("\n🚀 You can now run the Streamlit dashboard:")
        print("   streamlit run src/ui/dashboard.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
