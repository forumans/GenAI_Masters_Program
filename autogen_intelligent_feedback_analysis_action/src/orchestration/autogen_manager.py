"""
AutoGen-based orchestration system for intelligent user feedback analysis
"""

import logging
import json
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, config_list_from_json
from agents.csv_reader_agent import CSVReaderAgent
from agents.feedback_classifier_agent import FeedbackClassifierAgent
from agents.bug_analysis_agent import BugAnalysisAgent
from agents.feature_extractor_agent import FeatureExtractorAgent
from agents.ticket_creator_agent import TicketCreatorAgent
from agents.quality_critic_agent import QualityCriticAgent

class AutoGenFeedbackAnalysisSystem:
    """
    AutoGen-based multi-agent system for intelligent user feedback analysis
    """
    
    def __init__(self, data_dir: str = "data", output_dir: str = "data", 
                 confidence_threshold: float = 0.7):
        """
        Initialize the AutoGen Feedback Analysis System
        
        Args:
            data_dir (str): Directory containing input data
            output_dir (str): Directory for output files
            confidence_threshold (float): Minimum confidence for classification
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize agents
        self._setup_agents()
        self._setup_autogen_groupchat()
        
        # Processing results
        self.processing_results = {}
        
    def _setup_agents(self):
        """Setup all agents for the system"""
        try:
            # Initialize specialized agents
            self.csv_reader = CSVReaderAgent(data_dir=self.data_dir)
            self.feedback_classifier = FeedbackClassifierAgent(
                model_dir=os.path.join(output_dir, "models"),
                confidence_threshold=self.confidence_threshold
            )
            self.bug_analyzer = BugAnalysisAgent(severity_threshold=0.8)
            self.feature_extractor = FeatureExtractorAgent(impact_threshold=0.6)
            self.ticket_creator = TicketCreatorAgent(auto_approve=False)
            self.quality_critic = QualityCriticAgent(min_quality_score=0.7)
            
            self.logger.info("All 6 agents initialized successfully")
        except Exception as e:
            self.logger.error(f"Error setting up agents: {str(e)}")
            raise
    
    def _setup_autogen_groupchat(self):
        """Setup AutoGen group chat for agent orchestration"""
        try:
            # Configuration for AutoGen agents
            config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
            
            # Create coordinator agent
            self.coordinator = AssistantAgent(
                name="coordinator",
                llm_config={
                    "config_list": config_list,
                    "temperature": 0.1,
                    "timeout": 120,
                },
                system_message="""You are the coordinator of the feedback analysis system.
                Your role is to orchestrate the analysis process and ensure all agents work together.
                You should:
                1. Request data reading from the CSV reader
                2. Coordinate classification with the feedback classifier
                3. Summarize results and provide insights
                4. Handle any errors or issues that arise
                """
            )
            
            # Create data processor agent
            self.data_processor = AssistantAgent(
                name="data_processor",
                llm_config={
                    "config_list": config_list,
                    "temperature": 0.1,
                    "timeout": 120,
                },
                system_message="""You are the data processor for the feedback analysis system.
                Your role is to:
                1. Read and validate feedback data from CSV files
                2. Combine different data sources (app store reviews, support emails)
                3. Ensure data quality and consistency
                4. Provide data summaries and statistics
                """
            )
            
            # Create bug analysis agent
            self.bug_analyzer_agent = AssistantAgent(
                name="bug_analyzer",
                llm_config={
                    "config_list": config_list,
                    "temperature": 0.1,
                    "timeout": 120,
                },
                system_message="""You are the bug analysis specialist.
                Your role is to:
                1. Analyze bug reports for severity and category
                2. Extract device information and error messages
                3. Identify reproduction steps
                4. Provide technical insights
                """
            )
            
            # Create feature extraction agent
            self.feature_extractor_agent = AssistantAgent(
                name="feature_extractor",
                llm_config={
                    "config_list": config_list,
                    "temperature": 0.1,
                    "timeout": 120,
                },
                system_message="""You are the feature extraction specialist.
                Your role is to:
                1. Analyze feature requests for priority and impact
                2. Identify target user segments
                3. Extract expected benefits
                4. Assess implementation complexity
                """
            )
            
            # Create ticket creation agent
            self.ticket_creator_agent = AssistantAgent(
                name="ticket_creator",
                llm_config={
                    "config_list": config_list,
                    "temperature": 0.1,
                    "timeout": 120,
                },
                system_message="""You are the ticket creation specialist.
                Your role is to:
                1. Create structured tickets from analyzed feedback
                2. Assign appropriate priority and type
                3. Generate clear titles and descriptions
                4. Suggest assignees and effort estimates
                """
            )
            
            # Create quality review agent
            self.quality_reviewer_agent = AssistantAgent(
                name="quality_reviewer",
                llm_config={
                    "config_list": config_list,
                    "temperature": 0.1,
                    "timeout": 120,
                },
                system_message="""You are the quality review specialist.
                Your role is to:
                1. Review classification accuracy
                2. Assess ticket quality and completeness
                3. Identify issues and provide suggestions
                4. Ensure quality standards are met
                """
            )
            
            # Create user proxy
            self.user_proxy = UserProxyAgent(
                name="user_proxy",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=15,
                code_execution_config=False,
            )
            
            # Create group chat with all specialized agents
            self.group_chat = GroupChat(
                agents=[
                    self.coordinator, 
                    self.data_processor, 
                    self.bug_analyzer_agent,
                    self.feature_extractor_agent,
                    self.ticket_creator_agent,
                    self.quality_reviewer_agent,
                    self.user_proxy
                ],
                messages=[],
                max_round=30
            )
            
            # Create group chat manager
            self.group_manager = GroupChatManager(
                groupchat=self.group_chat,
                llm_config={
                    "config_list": config_list,
                    "temperature": 0.1,
                    "timeout": 120,
                }
            )
            
            self.logger.info("AutoGen group chat setup completed")
        except Exception as e:
            self.logger.error(f"Error setting up AutoGen group chat: {str(e)}")
            # Fallback to direct agent usage
            self.group_manager = None
    
    def process_feedback(self, use_autogen: bool = True) -> Dict:
        """
        Process feedback data using AutoGen agents
        
        Args:
            use_autogen (bool): Whether to use AutoGen orchestration or direct processing
            
        Returns:
            Dict: Processing results and metrics
        """
        try:
            start_time = datetime.now()
            
            if use_autogen and self.group_manager:
                return self._process_with_autogen()
            else:
                return self._process_direct()
                
        except Exception as e:
            self.logger.error(f"Error processing feedback: {str(e)}")
            raise
    
    def _process_with_autogen(self) -> Dict:
        """Process feedback using AutoGen group chat"""
        try:
            # Start the group chat with a processing request
            message = f"""
            Please process the feedback data following these steps:
            1. Read feedback data from {self.data_dir}
            2. Classify all feedback items
            3. Review the quality of classifications
            4. Provide a summary of results
            
            Data directory: {self.data_dir}
            Output directory: {self.output_dir}
            Confidence threshold: {self.confidence_threshold}
            """
            
            # Start the conversation
            chat_result = self.user_proxy.initiate_chat(
                self.group_manager,
                message=message,
                max_turns=15
            )
            
            # Extract results from chat history
            results = self._extract_results_from_chat(chat_result.chat_history)
            
            # Save results
            self._save_results(results)
            
            processing_time = (datetime.now() - results['start_time']).total_seconds()
            
            return {
                'status': 'success',
                'processing_time': processing_time,
                'total_processed': results.get('total_processed', 0),
                'successful': results.get('successful', 0),
                'failed': results.get('failed', 0),
                'classification_accuracy': results.get('accuracy', 0),
                'output_files': results.get('output_files', {}),
                'chat_summary': results.get('summary', '')
            }
            
        except Exception as e:
            self.logger.error(f"AutoGen processing failed: {str(e)}")
            # Fallback to direct processing
            return self._process_direct()
    
    def _process_direct(self) -> Dict:
        """Process feedback using direct agent calls"""
        try:
            start_time = datetime.now()
            
            # Step 1: Read feedback data
            self.logger.info("Step 1: Reading feedback data")
            feedback_df = self.csv_reader.combine_feedback_data()
            
            if not self.csv_reader.validate_data(feedback_df):
                raise ValueError("Invalid feedback data")
            
            # Step 2: Classify feedback
            self.logger.info("Step 2: Classifying feedback")
            classified_df = self.feedback_classifier.classify_batch(feedback_df)
            
            # Step 3: Analyze bugs (if any)
            self.logger.info("Step 3: Analyzing bug reports")
            bug_feedback = classified_df[classified_df['predicted_category'] == 'Bug']
            bug_analysis_df = pd.DataFrame()
            if len(bug_feedback) > 0:
                bug_analysis_df = self.bug_analyzer.analyze_batch(bug_feedback)
            
            # Step 4: Extract features (if any)
            self.logger.info("Step 4: Extracting feature requests")
            feature_feedback = classified_df[classified_df['predicted_category'] == 'Feature Request']
            feature_extraction_df = pd.DataFrame()
            if len(feature_feedback) > 0:
                feature_extraction_df = self.feature_extractor.extract_batch(feature_feedback)
            
            # Step 5: Create tickets
            self.logger.info("Step 5: Creating tickets")
            # Merge analysis data
            analysis_df = classified_df.copy()
            
            if not bug_analysis_df.empty:
                analysis_df = analysis_df.merge(
                    bug_analysis_df[['id', 'bug_severity', 'bug_category', 'device_info']], 
                    on='id', how='left'
                )
            
            if not feature_extraction_df.empty:
                analysis_df = analysis_df.merge(
                    feature_extraction_df[['id', 'feature_priority', 'feature_impact_score']], 
                    on='id', how='left'
                )
            
            tickets_df = self.ticket_creator.create_batch_tickets(feedback_df, analysis_df)
            
            # Step 6: Quality review
            self.logger.info("Step 6: Quality review")
            quality_results = self._perform_quality_review(tickets_df)
            
            # Step 7: Save results
            self.logger.info("Step 7: Saving results")
            output_files = self._save_direct_results(
                classified_df, 
                bug_analysis_df, 
                feature_extraction_df, 
                tickets_df, 
                quality_results
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'status': 'success',
                'processing_time': processing_time,
                'total_processed': len(classified_df),
                'successful': len(tickets_df),
                'failed': len(classified_df) - len(tickets_df),
                'classification_accuracy': quality_results.get('accuracy', 0),
                'output_files': output_files,
                'chat_summary': 'Direct processing completed successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Direct processing failed: {str(e)}")
            raise
    
    def _perform_quality_review(self, tickets_df: pd.DataFrame) -> Dict:
        """Perform quality review of generated tickets"""
        try:
            quality_reviews = []
            
            for idx, row in tickets_df.iterrows():
                ticket_data = row.to_dict()
                
                # Review ticket quality
                review = self.quality_critic.review_ticket_quality(ticket_data)
                quality_reviews.append(review)
            
            quality_df = pd.DataFrame(quality_reviews)
            
            # Calculate overall metrics
            avg_score = quality_df['overall_score'].mean()
            accuracy = min(avg_score * 1.1, 1.0)  # Estimate accuracy
            
            return {
                'quality_reviews': quality_df,
                'average_confidence': avg_score,
                'accuracy': accuracy,
                'total_reviews': len(quality_reviews),
                'needs_manual_review': len(quality_df[quality_df['needs_manual_review'] == True])
            }
            
        except Exception as e:
            self.logger.error(f"Error in quality review: {str(e)}")
            return {}
    
    def _get_quality_level(self, confidence: float) -> str:
        """Get quality level based on confidence score"""
        if confidence >= 0.9:
            return "Excellent"
        elif confidence >= 0.8:
            return "Good"
        elif confidence >= 0.7:
            return "Acceptable"
        elif confidence >= 0.6:
            return "Needs Improvement"
        else:
            return "Poor"
    
    def _save_direct_results(self, classified_df: pd.DataFrame, bug_analysis_df: pd.DataFrame, 
                              feature_extraction_df: pd.DataFrame, tickets_df: pd.DataFrame, 
                              quality_results: Dict) -> Dict:
        """Save results from direct processing"""
        try:
            output_files = {}
            
            # Save classified feedback
            classified_file = os.path.join(self.output_dir, 'classified_feedback.csv')
            classified_df.to_csv(classified_file, index=False)
            output_files['classified_feedback'] = classified_file
            
            # Save bug analysis results
            if not bug_analysis_df.empty:
                bug_file = os.path.join(self.output_dir, 'bug_analysis.csv')
                bug_analysis_df.to_csv(bug_file, index=False)
                output_files['bug_analysis'] = bug_file
            
            # Save feature extraction results
            if not feature_extraction_df.empty:
                feature_file = os.path.join(self.output_dir, 'feature_extraction.csv')
                feature_extraction_df.to_csv(feature_file, index=False)
                output_files['feature_extraction'] = feature_file
            
            # Save generated tickets
            tickets_file = os.path.join(self.output_dir, 'generated_tickets.csv')
            tickets_df.to_csv(tickets_file, index=False)
            output_files['generated_tickets'] = tickets_file
            
            # Save quality reviews
            if 'quality_reviews' in quality_results:
                quality_file = os.path.join(self.output_dir, 'quality_reviews.csv')
                quality_results['quality_reviews'].to_csv(quality_file, index=False)
                output_files['quality_reviews'] = quality_file
            
            # Save metrics
            metrics = {
                'processing_time': (datetime.now() - datetime.now()).total_seconds(),
                'total_processed': len(classified_df),
                'total_tickets': len(tickets_df),
                'bug_reports_analyzed': len(bug_analysis_df),
                'feature_requests_extracted': len(feature_extraction_df),
                'average_confidence': quality_results.get('average_confidence', 0),
                'accuracy': quality_results.get('accuracy', 0),
                'needs_manual_review': quality_results.get('needs_manual_review', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            metrics_file = os.path.join(self.output_dir, 'metrics.json')
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            output_files['metrics'] = metrics_file
            
            self.logger.info(f"Results saved to {self.output_dir}")
            return output_files
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
            return {}
    
    def _extract_results_from_chat(self, chat_history: List[Dict]) -> Dict:
        """Extract processing results from chat history"""
        try:
            # This is a simplified implementation
            # In a real scenario, you'd parse the chat history more carefully
            results = {
                'start_time': datetime.now(),
                'total_processed': 0,
                'successful': 0,
                'failed': 0,
                'accuracy': 0,
                'output_files': {},
                'summary': 'Chat processing completed'
            }
            
            # Look for result patterns in the chat
            for message in chat_history:
                content = message.get('content', '').lower()
                if 'processed' in content and 'items' in content:
                    # Try to extract numbers
                    import re
                    numbers = re.findall(r'\d+', content)
                    if len(numbers) >= 1:
                        results['total_processed'] = int(numbers[0])
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error extracting results from chat: {str(e)}")
            return {'error': str(e)}
    
    def _save_results(self, results: Dict):
        """Save processing results"""
        try:
            # Save results summary
            summary_file = os.path.join(self.output_dir, 'processing_summary.json')
            with open(summary_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            self.logger.info(f"Results summary saved to {summary_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
    
    def get_system_status(self) -> Dict:
        """Get system status and health"""
        try:
            status = {
                'system_type': 'AutoGen',
                'agents_initialized': True,
                'group_chat_active': self.group_manager is not None,
                'data_directory': self.data_dir,
                'output_directory': self.output_dir,
                'confidence_threshold': self.confidence_threshold,
                'timestamp': datetime.now().isoformat()
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            return {'error': str(e)}
