"""
Multi-agent orchestration system using CrewAI
"""

import logging
import json
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import sys
import os
from crewai import Crew, Task
from crewai.process import Process

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import all agents
from agents.csv_reader_agent import CSVReaderAgent
from agents.feedback_classifier_agent import FeedbackClassifierAgent
from agents.bug_analysis_agent import BugAnalysisAgent
from agents.feature_extractor_agent import FeatureExtractorAgent
from agents.ticket_creator_agent import TicketCreatorAgent
from agents.quality_critic_agent import QualityCriticAgent

class FeedbackAnalysisCrew:
    """
    Multi-agent system for intelligent user feedback analysis
    Orchestrates all agents to process feedback and generate tickets
    """
    
    def __init__(self, data_dir: str = "data", output_dir: str = "data", 
                 confidence_threshold: float = 0.7):
        """
        Initialize the multi-agent system
        
        Args:
            data_dir (str): Directory containing input data
            output_dir (str): Directory for output files
            confidence_threshold (float): Minimum confidence for classification
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)
        
        # Initialize all agents
        self.csv_reader = CSVReaderAgent(data_dir)
        self.feedback_classifier = FeedbackClassifierAgent(confidence_threshold=confidence_threshold)
        self.bug_analyzer = BugAnalysisAgent()
        self.feature_extractor = FeatureExtractorAgent()
        self.ticket_creator = TicketCreatorAgent(output_dir)
        self.quality_critic = QualityCriticAgent(min_confidence_threshold=confidence_threshold)
        
        # Processing statistics
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None,
            'processing_time': 0.0
        }
        
        # Create CrewAI crew
        self.crew = self._create_crew()
    
    def _create_crew(self) -> Crew:
        """Create the CrewAI crew with all agents and tasks"""
        
        # Define tasks
        read_data_task = Task(
            description="Read and parse feedback data from CSV files",
            agent=self.csv_reader.agent,
            expected_output="Parsed feedback data in DataFrame format"
        )
        
        classify_feedback_task = Task(
            description="Classify feedback into categories (Bug, Feature Request, Praise, Complaint, Spam)",
            agent=self.feedback_classifier.agent,
            expected_output="Feedback with classification results and confidence scores"
        )
        
        analyze_bugs_task = Task(
            description="Analyze bug reports and extract technical details, severity, and reproduction steps",
            agent=self.bug_analyzer.agent,
            expected_output="Detailed bug analysis with technical information"
        )
        
        extract_features_task = Task(
            description="Extract feature requests and assess user impact and business value",
            agent=self.feature_extractor.agent,
            expected_output="Feature analysis with impact assessment and priority scores"
        )
        
        create_tickets_task = Task(
            description="Generate structured tickets from analyzed feedback",
            agent=self.ticket_creator.agent,
            expected_output="Formatted tickets ready for review"
        )
        
        quality_review_task = Task(
            description="Review generated tickets for completeness and accuracy",
            agent=self.quality_critic.agent,
            expected_output="Quality assessment and approval/rejection recommendations"
        )
        
        # Create crew
        crew = Crew(
            agents=[
                self.csv_reader.agent,
                self.feedback_classifier.agent,
                self.bug_analyzer.agent,
                self.feature_extractor.agent,
                self.ticket_creator.agent,
                self.quality_critic.agent
            ],
            tasks=[
                read_data_task,
                classify_feedback_task,
                analyze_bugs_task,
                extract_features_task,
                create_tickets_task,
                quality_review_task
            ],
            process=Process.sequential,
            verbose=True
        )
        
        return crew
    
    def process_feedback_data(self, file_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process feedback data through the complete multi-agent pipeline
        
        Args:
            file_paths (Optional[List[str]]): Specific files to process, if None processes all
            
        Returns:
            Dict[str, Any]: Processing results and statistics
        """
        try:
            self.processing_stats['start_time'] = datetime.now()
            self.logger.info("Starting feedback analysis pipeline")
            
            # Step 1: Read data
            self.logger.info("Step 1: Reading feedback data")
            data_dict = self.csv_reader.process_all_data()
            
            combined_data = data_dict['combined']
            expected_data = data_dict['expected_classifications']
            
            self.logger.info(f"Loaded {len(combined_data)} feedback items")
            
            # Step 2: Classify feedback
            self.logger.info("Step 2: Classifying feedback")
            classified_data = self.feedback_classifier.classify_batch(combined_data)
            
            # Step 3: Analyze bugs and features separately
            self.logger.info("Step 3: Analyzing specific feedback types")
            
            # Separate bugs and features for specialized analysis
            bug_data = classified_data[classified_data['predicted_category'] == 'Bug']
            feature_data = classified_data[classified_data['predicted_category'] == 'Feature Request']
            
            # Analyze bugs
            analyzed_bugs = pd.DataFrame()
            if len(bug_data) > 0:
                analyzed_bugs = self.bug_analyzer.analyze_batch(bug_data)
                self.logger.info(f"Analyzed {len(analyzed_bugs)} bug reports")
            
            # Analyze features
            analyzed_features = pd.DataFrame()
            if len(feature_data) > 0:
                analyzed_features = self.feature_extractor.analyze_batch(feature_data)
                self.logger.info(f"Analyzed {len(analyzed_features)} feature requests")
            
            # Step 4: Merge analyses back
            self.logger.info("Step 4: Merging analysis results")
            final_data = self._merge_analyses(classified_data, analyzed_bugs, analyzed_features)
            
            # Step 5: Create tickets
            self.logger.info("Step 5: Creating tickets")
            tickets = self._create_tickets_from_data(final_data)
            
            # Step 6: Quality review
            self.logger.info("Step 6: Quality review")
            reviews = self.quality_critic.review_tickets_batch(tickets)
            
            # Step 7: Save results
            self.logger.info("Step 7: Saving results")
            self._save_processing_results(tickets, reviews, final_data)
            
            # Calculate final statistics
            self.processing_stats['end_time'] = datetime.now()
            self.processing_stats['processing_time'] = (
                self.processing_stats['end_time'] - self.processing_stats['start_time']
            ).total_seconds()
            self.processing_stats['total_processed'] = len(final_data)
            self.processing_stats['successful'] = len([r for r in reviews if not r.get('needs_manual_review', True)])
            self.processing_stats['failed'] = len([r for r in reviews if r.get('needs_manual_review', True)])
            
            # Generate final results
            results = {
                'processing_stats': self.processing_stats,
                'data_summary': self._generate_data_summary(final_data),
                'classification_stats': self.feedback_classifier.get_classification_stats(classified_data),
                'bug_analysis_stats': self.bug_analyzer.get_bug_analysis_stats(analyzed_bugs),
                'feature_analysis_stats': self.feature_extractor.get_feature_analysis_stats(analyzed_features),
                'ticket_stats': self.ticket_creator.get_ticket_stats(tickets),
                'quality_stats': self.quality_critic.get_quality_stats(reviews),
                'accuracy_evaluation': self._evaluate_accuracy(classified_data, expected_data)
            }
            
            self.logger.info(f"Processing completed successfully. Generated {len(tickets)} tickets")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in feedback processing pipeline: {str(e)}")
            self.processing_stats['end_time'] = datetime.now()
            self.processing_stats['failed'] = self.processing_stats['total_processed']
            raise
    
    def _merge_analyses(self, classified_data: pd.DataFrame, 
                       analyzed_bugs: pd.DataFrame, 
                       analyzed_features: pd.DataFrame) -> pd.DataFrame:
        """Merge specialized analyses back into classified data"""
        try:
            # Start with classified data
            final_data = classified_data.copy()
            
            # Add bug analysis
            if len(analyzed_bugs) > 0:
                bug_analysis_dict = analyzed_bugs.set_index('id')['bug_analysis'].to_dict()
                final_data['bug_analysis'] = final_data['id'].map(bug_analysis_dict)
                final_data['severity'] = final_data['id'].map(analyzed_bugs.set_index('id')['severity'])
                final_data['platform'] = final_data['id'].map(analyzed_bugs.set_index('id')['platform'])
                final_data['technical_details'] = final_data['id'].map(analyzed_bugs.set_index('id')['technical_details'])
            
            # Add feature analysis
            if len(analyzed_features) > 0:
                feature_analysis_dict = analyzed_features.set_index('id')['feature_analysis'].to_dict()
                final_data['feature_analysis'] = final_data['id'].map(feature_analysis_dict)
                final_data['feature_category'] = final_data['id'].map(analyzed_features.set_index('id')['feature_category'])
                final_data['feature_impact'] = final_data['id'].map(analyzed_features.set_index('id')['feature_impact'])
                final_data['feature_priority_score'] = final_data['id'].map(analyzed_features.set_index('id')['feature_priority_score'])
            
            # Fill missing analyses with empty dicts
            for col in ['bug_analysis', 'feature_analysis']:
                if col in final_data.columns:
                    final_data[col] = final_data[col].fillna('{}')
            
            return final_data
            
        except Exception as e:
            self.logger.error(f"Error merging analyses: {str(e)}")
            return classified_data
    
    def _create_tickets_from_data(self, final_data: pd.DataFrame) -> List[Dict]:
        """Create tickets from analyzed data"""
        try:
            tickets = []
            
            for _, row in final_data.iterrows():
                feedback_dict = row.to_dict()
                
                # Prepare analysis based on category
                analysis = {
                    'category': row.get('predicted_category', 'Unknown'),
                    'classification_confidence': row.get('classification_confidence', 0.0)
                }
                
                # Add specialized analysis
                if row.get('bug_analysis') and row.get('bug_analysis') != '{}':
                    bug_analysis = json.loads(row.get('bug_analysis', '{}'))
                    analysis.update(bug_analysis)
                
                if row.get('feature_analysis') and row.get('feature_analysis') != '{}':
                    feature_analysis = json.loads(row.get('feature_analysis', '{}'))
                    analysis.update(feature_analysis)
                
                # Create ticket
                ticket = self.ticket_creator.create_ticket(feedback_dict, analysis)
                tickets.append(ticket)
            
            return tickets
            
        except Exception as e:
            self.logger.error(f"Error creating tickets from data: {str(e)}")
            raise
    
    def _save_processing_results(self, tickets: List[Dict], reviews: List[Dict], 
                                final_data: pd.DataFrame):
        """Save all processing results to files"""
        try:
            # Save tickets
            self.ticket_creator.save_tickets_to_csv(tickets)
            
            # Save reviews
            reviews_df = pd.DataFrame(reviews)
            reviews_file = f"{self.output_dir}/quality_reviews.csv"
            reviews_df.to_csv(reviews_file, index=False)
            
            # Save final analyzed data
            final_data_file = f"{self.output_dir}/analyzed_feedback.csv"
            final_data.to_csv(final_data_file, index=False)
            
            # Save processing statistics
            stats_file = f"{self.output_dir}/metrics.csv"
            stats_data = {
                'metric': ['total_processed', 'successful_tickets', 'failed_tickets', 'processing_time_seconds'],
                'value': [
                    self.processing_stats['total_processed'],
                    self.processing_stats['successful'],
                    self.processing_stats['failed'],
                    self.processing_stats['processing_time']
                ]
            }
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_csv(stats_file, index=False)
            
            self.logger.info("All processing results saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving processing results: {str(e)}")
            raise
    
    def _generate_data_summary(self, final_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for processed data"""
        try:
            summary = {
                'total_feedback': len(final_data),
                'category_distribution': final_data['predicted_category'].value_counts().to_dict(),
                'source_type_distribution': final_data['source_type'].value_counts().to_dict(),
                'average_confidence': final_data['classification_confidence'].mean(),
                'high_confidence_count': len(final_data[final_data['classification_confidence'] >= self.confidence_threshold]),
                'processing_date': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating data summary: {str(e)}")
            return {}
    
    def _evaluate_accuracy(self, classified_data: pd.DataFrame, 
                          expected_data: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate classification accuracy against expected results"""
        try:
            if expected_data is None or len(expected_data) == 0:
                return {'error': 'No expected data available for evaluation'}
            
            evaluation = self.feedback_classifier.evaluate_classification(classified_data, expected_data)
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error evaluating accuracy: {str(e)}")
            return {'error': str(e)}
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status"""
        return {
            'status': 'Processing' if self.processing_stats['start_time'] and not self.processing_stats['end_time'] else 'Idle',
            'stats': self.processing_stats,
            'agents_status': {
                'csv_reader': 'Ready',
                'feedback_classifier': 'Ready',
                'bug_analyzer': 'Ready',
                'feature_extractor': 'Ready',
                'ticket_creator': 'Ready',
                'quality_critic': 'Ready'
            }
        }
    
    def run_custom_analysis(self, feedback_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run analysis on custom feedback data
        
        Args:
            feedback_data (pd.DataFrame): Custom feedback data
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            self.processing_stats['start_time'] = datetime.now()
            
            # Process through the pipeline
            classified_data = self.feedback_classifier.classify_batch(feedback_data)
            
            # Separate and analyze
            bug_data = classified_data[classified_data['predicted_category'] == 'Bug']
            feature_data = classified_data[classified_data['predicted_category'] == 'Feature Request']
            
            analyzed_bugs = pd.DataFrame()
            if len(bug_data) > 0:
                analyzed_bugs = self.bug_analyzer.analyze_batch(bug_data)
            
            analyzed_features = pd.DataFrame()
            if len(feature_data) > 0:
                analyzed_features = self.feature_extractor.analyze_batch(feature_data)
            
            final_data = self._merge_analyses(classified_data, analyzed_bugs, analyzed_features)
            tickets = self._create_tickets_from_data(final_data)
            reviews = self.quality_critic.review_tickets_batch(tickets)
            
            self.processing_stats['end_time'] = datetime.now()
            self.processing_stats['processing_time'] = (
                self.processing_stats['end_time'] - self.processing_stats['start_time']
            ).total_seconds()
            self.processing_stats['total_processed'] = len(final_data)
            
            return {
                'processed_data': final_data,
                'tickets': tickets,
                'reviews': reviews,
                'stats': self.processing_stats
            }
            
        except Exception as e:
            self.logger.error(f"Error in custom analysis: {str(e)}")
            raise
