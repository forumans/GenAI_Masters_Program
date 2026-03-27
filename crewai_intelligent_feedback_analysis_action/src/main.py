"""
Main application entry point for the Intelligent User Feedback Analysis System
"""

import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from orchestration.crew_manager import FeedbackAnalysisCrew

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler()
    ]
)

def setup_environment():
    """Setup environment variables and directories"""
    # Load environment variables
    load_dotenv()
    
    # Create necessary directories
    directories = ['data', 'logs', 'models']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please set up your .env file with the required variables.")
        return False
    
    return True

def run_system():
    """Run the complete feedback analysis system"""
    print("🧠 Intelligent User Feedback Analysis System")
    print("=" * 50)
    
    if not setup_environment():
        return
    
    try:
        # Initialize the system
        print("\n🚀 Initializing system...")
        crew_manager = FeedbackAnalysisCrew()
        
        # Process feedback data
        print("\n📊 Processing feedback data...")
        results = crew_manager.process_feedback_data()
        
        # Display results
        print("\n✅ Processing completed successfully!")
        print(f"📈 Total processed: {results['processing_stats']['total_processed']}")
        print(f"🎫 Tickets generated: {results['ticket_stats']['total_tickets']}")
        print(f"⏱️ Processing time: {results['processing_stats']['processing_time']:.2f} seconds")
        
        # Display accuracy if available
        accuracy = results.get('accuracy_evaluation', {}).get('overall_accuracy', 0)
        if accuracy > 0:
            print(f"🎯 Classification accuracy: {accuracy:.2%}")
        
        # Display category distribution
        if 'data_summary' in results:
            print("\n📊 Category Distribution:")
            for category, count in results['data_summary']['category_distribution'].items():
                print(f"  • {category}: {count}")
        
        # Display quality metrics
        if 'quality_stats' in results:
            quality_stats = results['quality_stats']
            print(f"\n✅ Quality Metrics:")
            print(f"  • Average quality score: {quality_stats['average_score']:.3f}")
            print(f"  • Tickets needing review: {quality_stats['tickets_need_review']}")
        
        print(f"\n📁 Results saved to data/ directory")
        print(f"🖥️  Run 'streamlit run src/ui/dashboard.py' to view the dashboard")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logging.error(f"System error: {str(e)}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "dashboard":
            # Launch Streamlit dashboard
            os.system("streamlit run src/ui/dashboard.py")
        elif command == "demo":
            # Run demonstration
            os.system("python run_demo.py")
        else:
            print("Usage:")
            print("  python src/main.py          - Run the system")
            print("  python src/main.py dashboard - Launch dashboard")
            print("  python src/main.py demo     - Run demonstration")
    else:
        # Run the system
        run_system()

if __name__ == "__main__":
    main()
