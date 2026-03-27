#!/usr/bin/env python3
"""
AutoGen Demo Script for Intelligent User Feedback Analysis System
"""

import logging
import os
import sys
import time
import json
from datetime import datetime
import pandas as pd

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from orchestration.autogen_manager import AutoGenFeedbackAnalysisSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print demo banner"""
    print("=" * 80)
    print("🤖 AUTOGEN INTELLIGENT USER FEEDBACK ANALYSIS SYSTEM")
    print("=" * 80)
    print("Multi-Agent AI System using AutoGen for Feedback Processing")
    print("=" * 80)

def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print('='*60)

def check_environment():
    """Check if environment is properly set up"""
    print_section("ENVIRONMENT CHECK")
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set up your .env file with a valid OpenAI API key")
        return False
    else:
        print("✅ OpenAI API key found")
    
    # Check data directory
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"❌ Data directory '{data_dir}' not found")
        return False
    else:
        print(f"✅ Data directory '{data_dir}' found")
    
    # Check data files
    required_files = ['app_store_reviews.csv', 'support_emails.csv']
    for file in required_files:
        file_path = os.path.join(data_dir, file)
        if not os.path.exists(file_path):
            print(f"❌ Required file '{file}' not found")
            return False
        else:
            print(f"✅ Required file '{file}' found")
    
    return True

def demo_data_reading(system):
    """Demo data reading functionality"""
    print_section("STEP 1: DATA READING")
    
    try:
        # Read feedback data
        feedback_df = system.csv_reader.combine_feedback_data()
        
        print(f"📊 Successfully read {len(feedback_df)} feedback items")
        print(f"   - App Store Reviews: {len(feedback_df[feedback_df['source_type'] == 'app_store_review'])}")
        print(f"   - Support Emails: {len(feedback_df[feedback_df['source_type'] == 'support_email'])}")
        
        # Display sample data
        print("\n📋 Sample Feedback Items:")
        for idx, row in feedback_df.head(3).iterrows():
            content_preview = row['content'][:100] + "..." if len(row['content']) > 100 else row['content']
            print(f"   [{row['id']}] {row['source_type']}: {content_preview}")
        
        return feedback_df
        
    except Exception as e:
        print(f"❌ Error reading data: {str(e)}")
        return None

def demo_classification(system, feedback_df):
    """Demo feedback classification"""
    print_section("STEP 2: FEEDBACK CLASSIFICATION")
    
    try:
        # Classify feedback
        print("🤖 Classifying feedback items...")
        classified_df = system.feedback_classifier.classify_batch(feedback_df)
        
        print(f"✅ Successfully classified {len(classified_df)} items")
        
        # Display classification results
        category_counts = classified_df['predicted_category'].value_counts()
        print("\n📊 Classification Distribution:")
        for category, count in category_counts.items():
            percentage = (count / len(classified_df)) * 100
            print(f"   - {category}: {count} ({percentage:.1f}%)")
        
        # Display confidence statistics
        avg_confidence = classified_df['classification_confidence'].mean()
        print(f"\n📈 Average Confidence: {avg_confidence:.3f}")
        
        # Show sample classifications
        print("\n🔍 Sample Classifications:")
        for idx, row in classified_df.head(3).iterrows():
            print(f"   [{row['id']}] {row['predicted_category']} (confidence: {row['classification_confidence']:.3f})")
            print(f"       Reasoning: {row['classification_reasoning']}")
        
        return classified_df
        
    except Exception as e:
        print(f"❌ Error in classification: {str(e)}")
        return None

def demo_autogen_orchestration(system):
    """Demo AutoGen orchestration"""
    print_section("STEP 3: AUTOGEN ORCHESTRATION")
    
    try:
        print("🚀 Starting AutoGen multi-agent processing...")
        print("   This will coordinate multiple agents to analyze feedback")
        
        # Process with AutoGen
        results = system.process_feedback(use_autogen=True)
        
        print(f"✅ AutoGen processing completed!")
        print(f"   - Status: {results['status']}")
        print(f"   - Processing Time: {results['processing_time']:.2f} seconds")
        print(f"   - Total Processed: {results['total_processed']}")
        print(f"   - Successful: {results['successful']}")
        print(f"   - Failed: {results['failed']}")
        print(f"   - Classification Accuracy: {results['classification_accuracy']:.2%}")
        
        return results
        
    except Exception as e:
        print(f"❌ AutoGen orchestration failed: {str(e)}")
        print("🔄 Falling back to direct processing...")
        
        try:
            results = system.process_feedback(use_autogen=False)
            print(f"✅ Direct processing completed!")
            return results
        except Exception as e2:
            print(f"❌ Direct processing also failed: {str(e2)}")
            return None

def demo_quality_review(results):
    """Demo quality review functionality"""
    print_section("STEP 4: QUALITY REVIEW")
    
    try:
        # Check if quality reviews were generated
        output_files = results.get('output_files', {})
        
        if 'quality_reviews' in output_files:
            quality_file = output_files['quality_reviews']
            if os.path.exists(quality_file):
                quality_df = pd.read_csv(quality_file)
                
                print(f"📋 Quality reviews completed for {len(quality_df)} items")
                
                # Quality distribution
                quality_counts = quality_df['quality_level'].value_counts()
                print("\n📊 Quality Distribution:")
                for level, count in quality_counts.items():
                    percentage = (count / len(quality_df)) * 100
                    print(f"   - {level}: {count} ({percentage:.1f}%)")
                
                # Items needing review
                needs_review = quality_df[quality_df['needs_manual_review'] == True]
                if len(needs_review) > 0:
                    print(f"\n⚠️  Items needing manual review: {len(needs_review)}")
                    print("   These items had low confidence scores and should be reviewed manually")
                else:
                    print("\n✅ No items require manual review")
                
        else:
            print("ℹ️  Quality reviews not available in this run")
        
    except Exception as e:
        print(f"❌ Error in quality review: {str(e)}")

def show_output_files(results):
    """Show generated output files"""
    print_section("OUTPUT FILES GENERATED")
    
    output_files = results.get('output_files', {})
    
    if not output_files:
        print("❌ No output files generated")
        return
    
    print(f"📁 Generated {len(output_files)} output files:")
    
    for file_type, file_path in output_files.items():
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"   ✅ {file_type}: {file_path} ({file_size:,} bytes)")
        else:
            print(f"   ❌ {file_type}: {file_path} (not found)")

def show_performance_metrics(results):
    """Show performance metrics"""
    print_section("PERFORMANCE METRICS")
    
    processing_time = results.get('processing_time', 0)
    total_processed = results.get('total_processed', 0)
    successful = results.get('successful', 0)
    accuracy = results.get('classification_accuracy', 0)
    
    if processing_time > 0 and total_processed > 0:
        throughput = total_processed / processing_time
        print(f"⚡ Processing Speed: {throughput:.2f} items/second")
    
    print(f"📊 Total Processed: {total_processed}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {total_processed - successful}")
    print(f"🎯 Classification Accuracy: {accuracy:.2%}")
    
    if total_processed > 0:
        success_rate = (successful / total_processed) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")

def main():
    """Main demo function"""
    print_banner()
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment setup failed. Please fix the issues above and try again.")
        return
    
    try:
        # Initialize AutoGen system
        print_section("INITIALIZING AUTOGEN SYSTEM")
        print("🤖 Setting up AutoGen agents and group chat...")
        
        system = AutoGenFeedbackAnalysisSystem(
            data_dir="data",
            output_dir="data",
            confidence_threshold=0.7
        )
        
        print("✅ AutoGen system initialized successfully!")
        
        # Show system status
        status = system.get_system_status()
        print(f"📋 System Status:")
        print(f"   - System Type: {status['system_type']}")
        print(f"   - Group Chat Active: {status['group_chat_active']}")
        print(f"   - Confidence Threshold: {status['confidence_threshold']}")
        
        # Demo 1: Data Reading
        feedback_df = demo_data_reading(system)
        if feedback_df is None:
            return
        
        # Demo 2: Classification
        classified_df = demo_classification(system, feedback_df)
        if classified_df is None:
            return
        
        # Demo 3: AutoGen Orchestration
        results = demo_autogen_orchestration(system)
        if results is None:
            return
        
        # Demo 4: Quality Review
        demo_quality_review(results)
        
        # Show results
        show_output_files(results)
        show_performance_metrics(results)
        
        # Final summary
        print_section("DEMO COMPLETION")
        print("🎉 AUTOGEN DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("\n📊 SUMMARY:")
        print(f"   - Processing Mode: AutoGen Multi-Agent System")
        print(f"   - Total Items Processed: {results.get('total_processed', 0)}")
        print(f"   - Processing Time: {results.get('processing_time', 0):.2f} seconds")
        print(f"   - Classification Accuracy: {results.get('classification_accuracy', 0):.2%}")
        
        print("\n🚀 NEXT STEPS:")
        print("   1. Check the data/ directory for generated output files")
        print("   2. Run 'streamlit run src/ui/dashboard.py' for interactive visualization")
        print("   3. Review quality reviews for items needing manual attention")
        print("   4. Adjust system parameters in configuration as needed")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        logger.exception("Demo execution failed")

if __name__ == "__main__":
    main()
