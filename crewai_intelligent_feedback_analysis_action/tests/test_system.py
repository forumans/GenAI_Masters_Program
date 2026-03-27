"""
Test suite for the Intelligent User Feedback Analysis System
"""

import unittest
import pandas as pd
import os
import sys
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.csv_reader_agent import CSVReaderAgent
from agents.feedback_classifier_agent import FeedbackClassifierAgent
from agents.bug_analysis_agent import BugAnalysisAgent
from agents.feature_extractor_agent import FeatureExtractorAgent
from agents.ticket_creator_agent import TicketCreatorAgent
from agents.quality_critic_agent import QualityCriticAgent
from orchestration.crew_manager import FeedbackAnalysisCrew

class TestCSVReaderAgent(unittest.TestCase):
    """Test cases for CSV Reader Agent"""
    
    def setUp(self):
        """Set up test environment"""
        self.agent = CSVReaderAgent("data")
    
    def test_read_app_store_reviews(self):
        """Test reading app store reviews"""
        try:
            df = self.agent.read_app_store_reviews()
            self.assertIsInstance(df, pd.DataFrame)
            self.assertGreater(len(df), 0)
            
            # Check required columns
            required_columns = ['review_id', 'platform', 'rating', 'review_text', 'user_name', 'date', 'app_version']
            for col in required_columns:
                self.assertIn(col, df.columns)
            
            print(f"✅ CSV Reader Agent: Read {len(df)} app store reviews")
            
        except Exception as e:
            self.fail(f"Error reading app store reviews: {str(e)}")
    
    def test_read_support_emails(self):
        """Test reading support emails"""
        try:
            df = self.agent.read_support_emails()
            self.assertIsInstance(df, pd.DataFrame)
            self.assertGreater(len(df), 0)
            
            # Check required columns
            required_columns = ['email_id', 'subject', 'body', 'sender_email', 'timestamp', 'priority']
            for col in required_columns:
                self.assertIn(col, df.columns)
            
            print(f"✅ CSV Reader Agent: Read {len(df)} support emails")
            
        except Exception as e:
            self.fail(f"Error reading support emails: {str(e)}")
    
    def test_combine_feedback_data(self):
        """Test combining feedback data"""
        try:
            combined_df = self.agent.combine_feedback_data()
            self.assertIsInstance(combined_df, pd.DataFrame)
            self.assertGreater(len(combined_df), 0)
            
            # Check combined structure
            self.assertIn('id', combined_df.columns)
            self.assertIn('source_type', combined_df.columns)
            self.assertIn('content', combined_df.columns)
            
            print(f"✅ CSV Reader Agent: Combined {len(combined_df)} feedback items")
            
        except Exception as e:
            self.fail(f"Error combining feedback data: {str(e)}")

class TestFeedbackClassifierAgent(unittest.TestCase):
    """Test cases for Feedback Classifier Agent"""
    
    def setUp(self):
        """Set up test environment"""
        self.agent = FeedbackClassifierAgent()
        
        # Load test data
        csv_reader = CSVReaderAgent("data")
        self.test_data = csv_reader.combine_feedback_data()
    
    def test_classify_single_feedback(self):
        """Test classifying a single feedback item"""
        try:
            # Test with a sample feedback
            sample_text = "App crashes when I try to sync my data. This has been happening since the last update."
            
            result = self.agent.classify_single_feedback(sample_text)
            
            self.assertIn('category', result)
            self.assertIn('confidence', result)
            self.assertIn('method', result)
            self.assertIn(result['category'], ['Bug', 'Feature Request', 'Praise', 'Complaint', 'Spam'])
            self.assertGreaterEqual(result['confidence'], 0.0)
            self.assertLessEqual(result['confidence'], 1.0)
            
            print(f"✅ Feedback Classifier: Classified as '{result['category']}' with {result['confidence']:.2f} confidence")
            
        except Exception as e:
            self.fail(f"Error classifying single feedback: {str(e)}")
    
    def test_classify_batch(self):
        """Test classifying batch feedback"""
        try:
            if len(self.test_data) > 0:
                classified_data = self.agent.classify_batch(self.test_data.head(5))  # Test with first 5 items
                
                self.assertIsInstance(classified_data, pd.DataFrame)
                self.assertEqual(len(classified_data), 5)
                
                # Check classification columns
                self.assertIn('predicted_category', classified_data.columns)
                self.assertIn('classification_confidence', classified_data.columns)
                self.assertIn('classification_method', classified_data.columns)
                
                print(f"✅ Feedback Classifier: Classified {len(classified_data)} feedback items")
                
            else:
                self.skipTest("No test data available")
                
        except Exception as e:
            self.fail(f"Error classifying batch feedback: {str(e)}")

class TestBugAnalysisAgent(unittest.TestCase):
    """Test cases for Bug Analysis Agent"""
    
    def setUp(self):
        """Set up test environment"""
        self.agent = BugAnalysisAgent()
        
        # Create test bug data
        self.test_bug_text = "App crashes when I try to sync my data. Using Android 12 on Samsung Galaxy S21. App version 3.2.1."
    
    def test_analyze_bug_report(self):
        """Test analyzing a bug report"""
        try:
            result = self.agent.analyze_bug_report(self.test_bug_text)
            
            self.assertIn('platform_info', result)
            self.assertIn('error_info', result)
            self.assertIn('reproduction_steps', result)
            self.assertIn('severity_assessment', result)
            self.assertIn('technical_details', result)
            
            # Check severity assessment
            severity = result['severity_assessment']['severity']
            self.assertIn(severity, ['Critical', 'High', 'Medium', 'Low'])
            
            print(f"✅ Bug Analysis: Analyzed bug with severity '{severity}'")
            
        except Exception as e:
            self.fail(f"Error analyzing bug report: {str(e)}")

class TestFeatureExtractorAgent(unittest.TestCase):
    """Test cases for Feature Extractor Agent"""
    
    def setUp(self):
        """Set up test environment"""
        self.agent = FeatureExtractorAgent()
        
        # Create test feature request
        self.test_feature_text = "Please add calendar integration functionality. This would be very helpful for my work."
    
    def test_analyze_feature_request(self):
        """Test analyzing a feature request"""
        try:
            result = self.agent.analyze_feature_request(self.test_feature_text)
            
            self.assertIn('feature_extraction', result)
            self.assertIn('category_info', result)
            self.assertIn('impact_assessment', result)
            self.assertIn('complexity_estimation', result)
            self.assertIn('business_value', result)
            self.assertIn('priority_score', result)
            
            # Check feature extraction
            is_feature = result['feature_extraction']['is_feature_request']
            self.assertTrue(is_feature)
            
            # Check priority score
            priority_score = result['priority_score']
            self.assertGreaterEqual(priority_score, 0.0)
            self.assertLessEqual(priority_score, 1.0)
            
            print(f"✅ Feature Extractor: Analyzed feature with priority score {priority_score:.2f}")
            
        except Exception as e:
            self.fail(f"Error analyzing feature request: {str(e)}")

class TestTicketCreatorAgent(unittest.TestCase):
    """Test cases for Ticket Creator Agent"""
    
    def setUp(self):
        """Set up test environment"""
        self.agent = TicketCreatorAgent("data")
        
        # Create test feedback data
        self.test_feedback = {
            'id': 'TEST001',
            'source_type': 'review',
            'content': 'App crashes when I try to sync my data.',
            'platform': 'Android',
            'app_version': '3.2.1',
            'user_name': 'Test User'
        }
        
        self.test_analysis = {
            'category': 'Bug',
            'classification_confidence': 0.85,
            'severity_assessment': {'severity': 'High'},
            'technical_details': 'Crash during data sync operation'
        }
    
    def test_create_ticket(self):
        """Test creating a ticket"""
        try:
            ticket = self.agent.create_ticket(self.test_feedback, self.test_analysis)
            
            self.assertIn('ticket_id', ticket)
            self.assertIn('title', ticket)
            self.assertIn('description', ticket)
            self.assertIn('category', ticket)
            self.assertIn('priority', ticket)
            self.assertIn('status', ticket)
            
            # Check ticket structure
            self.assertEqual(ticket['category'], 'Bug')
            self.assertEqual(ticket['status'], 'Open')
            self.assertTrue(ticket['ticket_id'].startswith('TK-'))
            
            print(f"✅ Ticket Creator: Created ticket {ticket['ticket_id']}")
            
        except Exception as e:
            self.fail(f"Error creating ticket: {str(e)}")

class TestQualityCriticAgent(unittest.TestCase):
    """Test cases for Quality Critic Agent"""
    
    def setUp(self):
        """Set up test environment"""
        self.agent = QualityCriticAgent()
        
        # Create test ticket
        self.test_ticket = {
            'ticket_id': 'TEST-TICKET-001',
            'title': 'Bug: App crashes during data sync',
            'description': 'App crashes when trying to sync data on Android 12. Version 3.2.1. Steps to reproduce: 1. Open app 2. Go to settings 3. Tap sync 4. App crashes.',
            'category': 'Bug',
            'priority': 'High',
            'status': 'Open',
            'classification_confidence': 0.85,
            'source_id': 'TEST001'
        }
    
    def test_review_ticket(self):
        """Test reviewing a ticket"""
        try:
            review = self.agent.review_ticket(self.test_ticket)
            
            self.assertIn('ticket_id', review)
            self.assertIn('overall_score', review)
            self.assertIn('quality_level', review)
            self.assertIn('needs_manual_review', review)
            self.assertIn('assessments', review)
            
            # Check score range
            score = review['overall_score']
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
            
            # Check quality level
            quality_level = review['quality_level']
            self.assertIn(quality_level, ['Excellent', 'Good', 'Acceptable', 'Needs Improvement', 'Poor'])
            
            print(f"✅ Quality Critic: Reviewed ticket with quality '{quality_level}' (score: {score:.3f})")
            
        except Exception as e:
            self.fail(f"Error reviewing ticket: {str(e)}")

class TestSystemIntegration(unittest.TestCase):
    """Test cases for system integration"""
    
    def test_complete_pipeline(self):
        """Test complete processing pipeline"""
        try:
            # Initialize crew manager
            crew_manager = FeedbackAnalysisCrew()
            
            # Process a small batch
            results = crew_manager.process_feedback_data()
            
            # Check results structure
            self.assertIn('processing_stats', results)
            self.assertIn('data_summary', results)
            self.assertIn('ticket_stats', results)
            
            # Check processing stats
            stats = results['processing_stats']
            self.assertGreater(stats['total_processed'], 0)
            self.assertGreater(stats['processing_time'], 0)
            
            print(f"✅ System Integration: Processed {stats['total_processed']} items in {stats['processing_time']:.2f}s")
            
        except Exception as e:
            self.fail(f"Error in complete pipeline test: {str(e)}")
    
    def test_accuracy_evaluation(self):
        """Test accuracy evaluation"""
        try:
            # Initialize components
            csv_reader = CSVReaderAgent("data")
            classifier = FeedbackClassifierAgent()
            
            # Load data
            data_dict = csv_reader.process_all_data()
            combined_data = data_dict['combined']
            expected_data = data_dict['expected_classifications']
            
            # Classify
            classified_data = classifier.classify_batch(combined_data)
            
            # Evaluate accuracy
            evaluation = classifier.evaluate_classification(classified_data, expected_data)
            
            if 'error' not in evaluation:
                self.assertIn('overall_accuracy', evaluation)
                self.assertGreaterEqual(evaluation['overall_accuracy'], 0.0)
                self.assertLessEqual(evaluation['overall_accuracy'], 1.0)
                
                accuracy = evaluation['overall_accuracy']
                print(f"✅ Accuracy Evaluation: Overall accuracy {accuracy:.2%}")
            else:
                print(f"⚠️ Accuracy Evaluation: {evaluation['error']}")
            
        except Exception as e:
            self.fail(f"Error in accuracy evaluation test: {str(e)}")

def run_system_validation():
    """Run complete system validation"""
    print("\n" + "="*80)
    print("🧪 INTELLIGENT USER FEEDBACK ANALYSIS SYSTEM - VALIDATION")
    print("="*80)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestCSVReaderAgent,
        TestFeedbackClassifierAgent,
        TestBugAnalysisAgent,
        TestFeatureExtractorAgent,
        TestTicketCreatorAgent,
        TestQualityCriticAgent,
        TestSystemIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 VALIDATION SUMMARY")
    print("="*80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n💥 ERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n✅ Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 SYSTEM VALIDATION: PASSED")
    else:
        print("⚠️ SYSTEM VALIDATION: NEEDS ATTENTION")
    
    print("="*80)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_system_validation()
