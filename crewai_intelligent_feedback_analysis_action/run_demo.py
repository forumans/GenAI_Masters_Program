"""
Demonstration script for the Intelligent User Feedback Analysis System
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

from orchestration.crew_manager import FeedbackAnalysisCrew
from agents.csv_reader_agent import CSVReaderAgent
from agents.feedback_classifier_agent import FeedbackClassifierAgent
from agents.bug_analysis_agent import BugAnalysisAgent
from agents.feature_extractor_agent import FeatureExtractorAgent
from agents.ticket_creator_agent import TicketCreatorAgent
from agents.quality_critic_agent import QualityCriticAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def print_banner():
    """Print demonstration banner"""
    print("\n" + "="*80)
    print("🧠 INTELLIGENT USER FEEDBACK ANALYSIS SYSTEM - DEMONSTRATION")
    print("="*80)
    print("This demo showcases the complete multi-agent system for analyzing user feedback")
    print("and generating structured tickets automatically.\n")

def demo_step_1_data_ingestion():
    """Demonstrate data ingestion"""
    print("📊 STEP 1: DATA INGESTION")
    print("-" * 40)
    
    try:
        # Initialize CSV Reader Agent
        csv_reader = CSVReaderAgent("data")
        
        # Read data
        print("📁 Reading feedback data from CSV files...")
        data_dict = csv_reader.process_all_data()
        
        # Display summary
        reviews = data_dict['reviews']
        emails = data_dict['emails']
        combined = data_dict['combined']
        
        print(f"✅ Successfully loaded data:")
        print(f"   • App Store Reviews: {len(reviews)}")
        print(f"   • Support Emails: {len(emails)}")
        print(f"   • Total Feedback Items: {len(combined)}")
        
        # Show sample data
        print("\n📋 Sample Feedback Items:")
        print("-" * 20)
        
        for idx, row in combined.head(3).iterrows():
            print(f"\nItem {idx + 1}:")
            print(f"  ID: {row['id']}")
            print(f"  Type: {row['source_type']}")
            print(f"  Content: {row['content'][:100]}...")
        
        return combined
        
    except Exception as e:
        print(f"❌ Error in data ingestion: {str(e)}")
        return None

def demo_step_2_classification():
    """Demonstrate feedback classification"""
    print("\n🔍 STEP 2: FEEDBACK CLASSIFICATION")
    print("-" * 40)
    
    try:
        # Load data from previous step
        csv_reader = CSVReaderAgent("data")
        data_dict = csv_reader.process_all_data()
        combined_data = data_dict['combined']
        
        # Initialize classifier
        classifier = FeedbackClassifierAgent()
        
        print("🤖 Classifying feedback using NLP...")
        classified_data = classifier.classify_batch(combined_data)
        
        # Display classification results
        print("✅ Classification completed!")
        
        category_dist = classified_data['predicted_category'].value_counts()
        print("\n📊 Classification Results:")
        print("-" * 20)
        
        for category, count in category_dist.items():
            percentage = (count / len(classified_data)) * 100
            print(f"   • {category}: {count} ({percentage:.1f}%)")
        
        # Show sample classifications
        print("\n🔍 Sample Classifications:")
        print("-" * 25)
        
        for idx, row in classified_data.head(3).iterrows():
            print(f"\nFeedback {row['id']}:")
            print(f"  Content: {row['content'][:80]}...")
            print(f"  Predicted: {row['predicted_category']}")
            print(f"  Confidence: {row['classification_confidence']:.2f}")
            print(f"  Method: {row['classification_method']}")
        
        return classified_data
        
    except Exception as e:
        print(f"❌ Error in classification: {str(e)}")
        return None

def demo_step_3_specialized_analysis():
    """Demonstrate specialized analysis for bugs and features"""
    print("\n🔬 STEP 3: SPECIALIZED ANALYSIS")
    print("-" * 40)
    
    try:
        # Load classified data
        csv_reader = CSVReaderAgent("data")
        classifier = FeedbackClassifierAgent()
        data_dict = csv_reader.process_all_data()
        combined_data = data_dict['combined']
        classified_data = classifier.classify_batch(combined_data)
        
        # Separate bugs and features
        bug_data = classified_data[classified_data['predicted_category'] == 'Bug']
        feature_data = classified_data[classified_data['predicted_category'] == 'Feature Request']
        
        print(f"🐛 Analyzing {len(bug_data)} bug reports...")
        print(f"💡 Analyzing {len(feature_data)} feature requests...")
        
        # Analyze bugs
        if len(bug_data) > 0:
            bug_analyzer = BugAnalysisAgent()
            analyzed_bugs = bug_analyzer.analyze_batch(bug_data)
            
            print("✅ Bug analysis completed!")
            
            # Show bug analysis sample
            print("\n🐛 Sample Bug Analysis:")
            print("-" * 25)
            
            sample_bug = analyzed_bugs.iloc[0]
            print(f"Bug ID: {sample_bug['id']}")
            print(f"Severity: {sample_bug['severity']}")
            print(f"Platform: {sample_bug['platform']}")
            print(f"Technical Details: {sample_bug['technical_details'][:100]}...")
        
        # Analyze features
        if len(feature_data) > 0:
            feature_extractor = FeatureExtractorAgent()
            analyzed_features = feature_extractor.analyze_batch(feature_data)
            
            print("✅ Feature analysis completed!")
            
            # Show feature analysis sample
            print("\n💡 Sample Feature Analysis:")
            print("-" * 30)
            
            sample_feature = analyzed_features.iloc[0]
            print(f"Feature ID: {sample_feature['id']}")
            print(f"Category: {sample_feature['feature_category']}")
            print(f"Impact: {sample_feature['feature_impact']}")
            print(f"Priority Score: {sample_feature['feature_priority_score']}")
            print(f"Summary: {sample_feature['feature_summary'][:100]}...")
        
        return classified_data, analyzed_bugs if len(bug_data) > 0 else pd.DataFrame(), analyzed_features if len(feature_data) > 0 else pd.DataFrame()
        
    except Exception as e:
        print(f"❌ Error in specialized analysis: {str(e)}")
        return None, None, None

def demo_step_4_ticket_creation():
    """Demonstrate ticket creation"""
    print("\n🎫 STEP 4: TICKET CREATION")
    print("-" * 40)
    
    try:
        # Run previous steps to get data
        csv_reader = CSVReaderAgent("data")
        classifier = FeedbackClassifierAgent()
        bug_analyzer = BugAnalysisAgent()
        feature_extractor = FeatureExtractorAgent()
        
        data_dict = csv_reader.process_all_data()
        combined_data = data_dict['combined']
        classified_data = classifier.classify_batch(combined_data)
        
        # Specialized analysis
        bug_data = classified_data[classified_data['predicted_category'] == 'Bug']
        feature_data = classified_data[classified_data['predicted_category'] == 'Feature Request']
        
        analyzed_bugs = pd.DataFrame()
        analyzed_features = pd.DataFrame()
        
        if len(bug_data) > 0:
            analyzed_bugs = bug_analyzer.analyze_batch(bug_data)
        if len(feature_data) > 0:
            analyzed_features = feature_extractor.analyze_batch(feature_data)
        
        # Merge analyses
        final_data = classified_data.copy()
        
        if len(analyzed_bugs) > 0:
            bug_analysis_dict = analyzed_bugs.set_index('id')['bug_analysis'].to_dict()
            final_data['bug_analysis'] = final_data['id'].map(bug_analysis_dict)
            final_data['severity'] = final_data['id'].map(analyzed_bugs.set_index('id')['severity'])
        
        if len(analyzed_features) > 0:
            feature_analysis_dict = analyzed_features.set_index('id')['feature_analysis'].to_dict()
            final_data['feature_analysis'] = final_data['id'].map(feature_analysis_dict)
            final_data['feature_category'] = final_data['id'].map(analyzed_features.set_index('id')['feature_category'])
        
        # Create tickets
        print("🎫 Generating structured tickets...")
        ticket_creator = TicketCreatorAgent("data")
        
        tickets = []
        for _, row in final_data.iterrows():
            feedback_dict = row.to_dict()
            
            analysis = {
                'category': row.get('predicted_category', 'Unknown'),
                'classification_confidence': row.get('classification_confidence', 0.0)
            }
            
            if row.get('bug_analysis') and row.get('bug_analysis') != '{}':
                bug_analysis = json.loads(row.get('bug_analysis', '{}'))
                analysis.update(bug_analysis)
            
            if row.get('feature_analysis') and row.get('feature_analysis') != '{}':
                feature_analysis = json.loads(row.get('feature_analysis', '{}'))
                analysis.update(feature_analysis)
            
            ticket = ticket_creator.create_ticket(feedback_dict, analysis)
            tickets.append(ticket)
        
        print(f"✅ Generated {len(tickets)} tickets!")
        
        # Save tickets
        ticket_creator.save_tickets_to_csv(tickets)
        
        # Show sample tickets
        print("\n🎫 Sample Tickets:")
        print("-" * 20)
        
        for i, ticket in enumerate(tickets[:3]):
            print(f"\nTicket {i+1}:")
            print(f"  ID: {ticket['ticket_id']}")
            print(f"  Title: {ticket['title']}")
            print(f"  Category: {ticket['category']}")
            print(f"  Priority: {ticket['priority']}")
            print(f"  Status: {ticket['status']}")
        
        return tickets
        
    except Exception as e:
        print(f"❌ Error in ticket creation: {str(e)}")
        return None

def demo_step_5_quality_review():
    """Demonstrate quality review"""
    print("\n✅ STEP 5: QUALITY REVIEW")
    print("-" * 40)
    
    try:
        # Load tickets from previous step
        ticket_creator = TicketCreatorAgent("data")
        
        # Read generated tickets
        if os.path.exists("data/generated_tickets.csv"):
            tickets_df = pd.read_csv("data/generated_tickets.csv")
            tickets = tickets_df.to_dict('records')
        else:
            print("❌ No tickets found. Please run previous steps first.")
            return None
        
        print(f"🔍 Reviewing {len(tickets)} tickets for quality...")
        
        # Quality review
        quality_critic = QualityCriticAgent()
        reviews = quality_critic.review_tickets_batch(tickets)
        
        print("✅ Quality review completed!")
        
        # Quality statistics
        quality_stats = quality_critic.get_quality_stats(reviews)
        
        print("\n📊 Quality Statistics:")
        print("-" * 25)
        print(f"   • Average Score: {quality_stats['average_score']:.3f}")
        print(f"   • Median Score: {quality_stats['median_score']:.3f}")
        print(f"   • Tickets Needing Review: {quality_stats['tickets_need_review']}")
        
        print("\n📊 Quality Level Distribution:")
        print("-" * 35)
        for level, count in quality_stats['quality_level_distribution'].items():
            print(f"   • {level}: {count}")
        
        # Show sample reviews
        print("\n🔍 Sample Quality Reviews:")
        print("-" * 30)
        
        for i, review in enumerate(reviews[:3]):
            print(f"\nReview {i+1}:")
            print(f"  Ticket ID: {review['ticket_id']}")
            print(f"  Quality Level: {review['quality_level']}")
            print(f"  Score: {review['overall_score']:.3f}")
            print(f"  Needs Manual Review: {'Yes' if review['needs_manual_review'] else 'No'}")
            
            if review['issues']:
                print(f"  Issues: {review['issues'][0] if review['issues'] else 'None'}")
        
        # Save reviews
        reviews_df = pd.DataFrame(reviews)
        reviews_df.to_csv("data/quality_reviews.csv", index=False)
        
        return reviews
        
    except Exception as e:
        print(f"❌ Error in quality review: {str(e)}")
        return None

def demo_step_6_accuracy_evaluation():
    """Demonstrate accuracy evaluation"""
    print("\n🎯 STEP 6: ACCURACY EVALUATION")
    print("-" * 40)
    
    try:
        # Load data
        csv_reader = CSVReaderAgent("data")
        classifier = FeedbackClassifierAgent()
        
        data_dict = csv_reader.process_all_data()
        combined_data = data_dict['combined']
        expected_data = data_dict['expected_classifications']
        
        # Classify
        classified_data = classifier.classify_batch(combined_data)
        
        # Evaluate accuracy
        print("🎯 Evaluating classification accuracy...")
        evaluation = classifier.evaluate_classification(classified_data, expected_data)
        
        if 'error' in evaluation:
            print(f"⚠️ Could not evaluate accuracy: {evaluation['error']}")
            return
        
        print("✅ Accuracy evaluation completed!")
        
        print("\n📊 Accuracy Results:")
        print("-" * 20)
        print(f"   • Overall Accuracy: {evaluation['overall_accuracy']:.2%}")
        print(f"   • Total Evaluated: {evaluation['total_evaluated']}")
        print(f"   • Correct Predictions: {evaluation['correct_predictions']}")
        
        print("\n📊 Category-wise Accuracy:")
        print("-" * 30)
        
        for category, accuracy in evaluation['category_accuracy'].items():
            print(f"   • {category}: {accuracy:.2%}")
        
        # Show misclassified items
        if evaluation['misclassified']:
            print(f"\n❌ Misclassified Items (showing first 3):")
            print("-" * 45)
            
            for i, item in enumerate(evaluation['misclassified'][:3]):
                print(f"\nItem {i+1}:")
                print(f"  ID: {item['source_id']}")
                print(f"  Predicted: {item['predicted_category']}")
                print(f"  Expected: {item['category']}")
                print(f"  Confidence: {item['classification_confidence']:.2f}")
        
        return evaluation
        
    except Exception as e:
        print(f"❌ Error in accuracy evaluation: {str(e)}")
        return None

def demo_complete_system():
    """Demonstrate the complete system"""
    print("\n🚀 COMPLETE SYSTEM DEMONSTRATION")
    print("-" * 40)
    
    try:
        start_time = time.time()
        
        # Initialize the complete system
        print("🤖 Initializing complete multi-agent system...")
        crew_manager = FeedbackAnalysisCrew()
        
        # Process all data
        print("📊 Processing feedback through complete pipeline...")
        results = crew_manager.process_feedback_data()
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print("✅ Complete system processing finished!")
        
        # Display comprehensive results
        print(f"\n📊 SYSTEM PERFORMANCE:")
        print("-" * 25)
        print(f"   • Total Processed: {results['processing_stats']['total_processed']}")
        print(f"   • Successful: {results['processing_stats']['successful']}")
        print(f"   • Failed: {results['processing_stats']['failed']}")
        print(f"   • Processing Time: {processing_time:.2f} seconds")
        print(f"   • Items/Second: {results['processing_stats']['total_processed']/processing_time:.2f}")
        
        if 'accuracy_evaluation' in results and 'overall_accuracy' in results['accuracy_evaluation']:
            accuracy = results['accuracy_evaluation']['overall_accuracy']
            print(f"   • Classification Accuracy: {accuracy:.2%}")
        
        print(f"\n📊 OUTPUT FILES GENERATED:")
        print("-" * 30)
        
        output_files = [
            "data/generated_tickets.csv",
            "data/quality_reviews.csv", 
            "data/metrics.csv",
            "data/analyzed_feedback.csv",
            "data/processing_log.csv"
        ]
        
        for file_path in output_files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"   ✅ {file_path} ({size:,} bytes)")
            else:
                print(f"   ❌ {file_path} (not found)")
        
        print(f"\n🎯 READY FOR USE!")
        print("-" * 20)
        print(f"   • Run 'streamlit run src/ui/dashboard.py' to view the interactive dashboard")
        print(f"   • Check the data/ directory for all generated files")
        print(f"   • Review the quality reviews for any tickets needing manual attention")
        
        return results
        
    except Exception as e:
        print(f"❌ Error in complete system demo: {str(e)}")
        return None

def main():
    """Main demonstration function"""
    print_banner()
    
    print("Select demonstration mode:")
    print("1. Step-by-step demonstration (recommended)")
    print("2. Complete system demonstration")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🎬 STEP-BY-STEP DEMONSTRATION")
            print("=" * 50)
            
            # Run each step
            step1_result = demo_step_1_data_ingestion()
            if step1_result is None:
                return
            
            input("\nPress Enter to continue to Step 2...")
            step2_result = demo_step_2_classification()
            if step2_result is None:
                return
            
            input("\nPress Enter to continue to Step 3...")
            step3_results = demo_step_3_specialized_analysis()
            if step3_results[0] is None:
                return
            
            input("\nPress Enter to continue to Step 4...")
            step4_result = demo_step_4_ticket_creation()
            if step4_result is None:
                return
            
            input("\nPress Enter to continue to Step 5...")
            step5_result = demo_step_5_quality_review()
            if step5_result is None:
                return
            
            input("\nPress Enter to continue to Step 6...")
            step6_result = demo_step_6_accuracy_evaluation()
            
            print("\n🎉 STEP-BY-STEP DEMONSTRATION COMPLETED!")
            
        elif choice == "2":
            print("\n🚀 COMPLETE SYSTEM DEMONSTRATION")
            print("=" * 50)
            
            demo_complete_system()
            
        elif choice == "3":
            print("\n👋 Goodbye!")
            return
            
        else:
            print("\n❌ Invalid choice. Please run the demo again.")
            return
        
        print(f"\n🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print(f"📊 Check the data/ directory for all generated output files")
        print(f"🖥️  Run 'streamlit run src/ui/dashboard.py' to view the interactive dashboard")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Demonstration error: {str(e)}")

if __name__ == "__main__":
    main()
