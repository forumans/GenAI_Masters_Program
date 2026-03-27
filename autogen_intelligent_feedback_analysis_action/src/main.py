#!/usr/bin/env python3
"""
Main entry point for AutoGen Intelligent User Feedback Analysis System
"""

import logging
import os
import sys
import argparse
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from orchestration.autogen_manager import AutoGenFeedbackAnalysisSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='AutoGen Intelligent Feedback Analysis System')
    parser.add_argument('--data-dir', default='data', help='Data directory path')
    parser.add_argument('--output-dir', default='data', help='Output directory path')
    parser.add_argument('--confidence-threshold', type=float, default=0.7, 
                       help='Classification confidence threshold')
    parser.add_argument('--use-autogen', action='store_true', default=True,
                       help='Use AutoGen orchestration (default: True)')
    parser.add_argument('--demo', action='store_true', help='Run demo mode')
    
    args = parser.parse_args()
    
    print("🤖 AutoGen Intelligent User Feedback Analysis System")
    print("=" * 60)
    
    try:
        # Initialize system
        print("🚀 Initializing AutoGen system...")
        system = AutoGenFeedbackAnalysisSystem(
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            confidence_threshold=args.confidence_threshold
        )
        
        # Show system status
        status = system.get_system_status()
        print(f"✅ System initialized successfully!")
        print(f"   - System Type: {status['system_type']}")
        print(f"   - Group Chat Active: {status['group_chat_active']}")
        print(f"   - Data Directory: {status['data_directory']}")
        print(f"   - Output Directory: {status['output_directory']}")
        
        if args.demo:
            print("\n🎯 Running in demo mode...")
            # Demo mode would run a simplified version
            print("Demo mode would run here. Use run_autogen_demo.py for full demo.")
        
        # Process feedback
        print(f"\n📊 Processing feedback data...")
        print(f"   - Using AutoGen: {args.use_autogen}")
        print(f"   - Confidence Threshold: {args.confidence_threshold}")
        
        results = system.process_feedback(use_autogen=args.use_autogen)
        
        # Display results
        print(f"\n✅ Processing completed!")
        print(f"   - Status: {results['status']}")
        print(f"   - Processing Time: {results['processing_time']:.2f} seconds")
        print(f"   - Total Processed: {results['total_processed']}")
        print(f"   - Successful: {results['successful']}")
        print(f"   - Classification Accuracy: {results['classification_accuracy']:.2%}")
        
        # Show output files
        output_files = results.get('output_files', {})
        if output_files:
            print(f"\n📁 Output files generated:")
            for file_type, file_path in output_files.items():
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"   - {file_type}: {file_path} ({file_size:,} bytes)")
        
        print(f"\n🎉 AutoGen analysis completed successfully!")
        print(f"📊 Check the {args.output_dir} directory for all generated files")
        
    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Main execution failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
