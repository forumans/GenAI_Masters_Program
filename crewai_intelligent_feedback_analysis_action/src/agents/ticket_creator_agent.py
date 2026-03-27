"""
Ticket Creator Agent - Generates structured tickets and logs them to output CSV files
"""

import pandas as pd
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid
import re
from enum import Enum
from crewai import Agent
from langchain_openai import ChatOpenAI

class TicketStatus(Enum):
    """Ticket status values"""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    PENDING_REVIEW = "Pending Review"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class TicketPriority(Enum):
    """Ticket priority levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class TicketCreatorAgent:
    """
    Agent responsible for generating structured tickets from analyzed feedback:
    - Creates standardized ticket format
    - Assigns appropriate priority
    - Generates ticket titles
    - Creates detailed descriptions
    - Logs tickets to CSV files
    """
    
    def __init__(self, output_dir: str = "data"):
        """
        Initialize the Ticket Creator Agent
        
        Args:
            output_dir (str): Directory for output files
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
        
        # Output file paths
        self.tickets_file = f"{output_dir}/generated_tickets.csv"
        self.logs_file = f"{output_dir}/processing_log.csv"
        
        # Ticket templates
        self.ticket_templates = {
            'Bug': {
                'title_template': "Bug: {issue} on {platform}",
                'description_template': "BUG REPORT\n\nUser Impact: {impact}\nPlatform: {platform}\nApp Version: {version}\n\nDescription:\n{description}\n\nTechnical Details:\n{technical_details}\n\nSteps to Reproduce:\n{reproduction_steps}\n\nSeverity Assessment: {severity}",
                'tags': ['bug', 'technical', 'reproducible']
            },
            'Feature Request': {
                'title_template': "Feature Request: {feature}",
                'description_template': "FEATURE REQUEST\n\nCategory: {category}\nUser Impact: {impact}\nBusiness Value: {business_value}\n\nDescription:\n{description}\n\nFeature Details:\n{feature_summary}\n\nImplementation Complexity: {complexity}\nPriority Score: {priority_score}",
                'tags': ['feature-request', 'enhancement', 'user-feedback']
            },
            'Praise': {
                'title_template': "Positive Feedback: {aspect}",
                'description_template': "POSITIVE FEEDBACK\n\nUser Sentiment: {sentiment}\nPlatform: {platform}\nApp Version: {version}\n\nFeedback:\n{description}\n\nKey Positive Points:\n{positive_points}",
                'tags': ['praise', 'positive-feedback', 'satisfaction']
            },
            'Complaint': {
                'title_template': "Complaint: {issue}",
                'description_template': "USER COMPLAINT\n\nIssue Type: {issue_type}\nUser Impact: {impact}\nPlatform: {platform}\n\nDescription:\n{description}\n\nComplaint Details:\n{complaint_details}\n\nSuggested Actions:\n{suggested_actions}",
                'tags': ['complaint', 'user-concern', 'attention-needed']
            },
            'Spam': {
                'title_template': "Spam/Irrelevant: {reason}",
                'description_template': "SPAM/IRRELEVANT FEEDBACK\n\nReason for Classification: {reason}\nOriginal Content:\n{description}\n\nAction: No action required",
                'tags': ['spam', 'irrelevant', 'ignore']
            }
        }
        
        # Priority mapping
        self.priority_mapping = {
            'Bug': {
                'Critical': TicketPriority.CRITICAL.value,
                'High': TicketPriority.HIGH.value,
                'Medium': TicketPriority.MEDIUM.value,
                'Low': TicketPriority.LOW.value
            },
            'Feature Request': {
                'Critical': TicketPriority.HIGH.value,  # Features rarely critical
                'High': TicketPriority.HIGH.value,
                'Medium': TicketPriority.MEDIUM.value,
                'Low': TicketPriority.LOW.value
            },
            'Praise': {
                'Critical': TicketPriority.LOW.value,
                'High': TicketPriority.LOW.value,
                'Medium': TicketPriority.LOW.value,
                'Low': TicketPriority.LOW.value
            },
            'Complaint': {
                'Critical': TicketPriority.HIGH.value,
                'High': TicketPriority.MEDIUM.value,
                'Medium': TicketPriority.MEDIUM.value,
                'Low': TicketPriority.LOW.value
            },
            'Spam': {
                'Critical': TicketPriority.LOW.value,
                'High': TicketPriority.LOW.value,
                'Medium': TicketPriority.LOW.value,
                'Low': TicketPriority.LOW.value
            }
        }
        
        # Create CrewAI agent
        self.agent = Agent(
            role="Ticket Creation Specialist",
            goal="Generate structured, well-formatted tickets from analyzed user feedback",
            backstory="You are an expert technical support specialist with deep experience in creating clear, actionable tickets from user feedback.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def generate_ticket_id(self) -> str:
        """
        Generate a unique ticket ID
        
        Returns:
            str: Unique ticket ID
        """
        timestamp = datetime.now().strftime("%Y%m%d")
        random_part = str(uuid.uuid4())[:8].upper()
        return f"TK-{timestamp}-{random_part}"
    
    def generate_ticket_title(self, category: str, content: str, analysis: Dict) -> str:
        """
        Generate a clear, actionable ticket title
        
        Args:
            category (str): Feedback category
            content (str): Original content
            analysis (Dict): Analysis results
            
        Returns:
            str: Ticket title
        """
        try:
            # Extract key information based on category
            if category == 'Bug':
                # Extract main issue from content
                issue_keywords = ['crash', 'freeze', 'login', 'sync', 'error', 'bug', 'issue']
                for keyword in issue_keywords:
                    if keyword in content.lower():
                        issue = keyword.replace('_', ' ').title()
                        break
                else:
                    issue = "Technical Issue"
                
                platform = analysis.get('platform_info', {}).get('platform', 'Unknown')
                return f"Bug: {issue} on {platform}"
            
            elif category == 'Feature Request':
                feature_summary = analysis.get('feature_summary', 'New Feature')
                # Extract key feature
                if ':' in feature_summary:
                    feature = feature_summary.split(':')[1].strip()
                else:
                    feature = feature_summary
                return f"Feature Request: {feature[:50]}..." if len(feature) > 50 else f"Feature Request: {feature}"
            
            elif category == 'Praise':
                # Extract what user is praising
                positive_words = ['ui', 'feature', 'performance', 'design', 'functionality']
                for word in positive_words:
                    if word in content.lower():
                        aspect = word.title()
                        break
                else:
                    aspect = "General"
                return f"Positive Feedback: {aspect}"
            
            elif category == 'Complaint':
                # Extract complaint type
                complaint_keywords = ['price', 'slow', 'service', 'performance', 'usability']
                for keyword in complaint_keywords:
                    if keyword in content.lower():
                        issue_type = keyword.title()
                        break
                else:
                    issue_type = "User Concern"
                return f"Complaint: {issue_type}"
            
            elif category == 'Spam':
                return "Spam/Irrelevant: Automated Classification"
            
            else:
                return f"General Feedback: {category}"
                
        except Exception as e:
            self.logger.error(f"Error generating ticket title: {str(e)}")
            return f"Feedback: {category}"
    
    def generate_ticket_description(self, category: str, content: str, analysis: Dict, source_info: Dict) -> str:
        """
        Generate detailed ticket description
        
        Args:
            category (str): Feedback category
            content (str): Original content
            analysis (Dict): Analysis results
            source_info (Dict): Source information
            
        Returns:
            str: Detailed ticket description
        """
        try:
            template = self.ticket_templates.get(category, self.ticket_templates['Bug'])
            
            # Prepare template variables
            template_vars = {
                'description': content,
                'platform': source_info.get('platform', 'Unknown'),
                'version': source_info.get('app_version', 'Unknown'),
                'impact': analysis.get('impact_assessment', {}).get('impact_level', 'Unknown'),
                'severity': analysis.get('severity_assessment', {}).get('severity', 'Unknown'),
                'technical_details': analysis.get('technical_details', 'Not provided'),
                'reproduction_steps': self._format_reproduction_steps(analysis.get('reproduction_steps', {})),
                'category': analysis.get('category_info', {}).get('category', 'Unknown'),
                'feature_summary': analysis.get('feature_summary', 'Not provided'),
                'business_value': analysis.get('business_value', {}).get('value', 'Unknown'),
                'complexity': analysis.get('complexity_estimation', {}).get('complexity', 'Unknown'),
                'priority_score': analysis.get('priority_score', 0.0),
                'sentiment': analysis.get('sentiment_analysis', {}).get('sentiment_label', 'Unknown'),
                'positive_points': self._extract_positive_points(content),
                'issue_type': self._extract_issue_type(content),
                'complaint_details': self._extract_complaint_details(content),
                'suggested_actions': self._generate_suggested_actions(category, analysis),
                'reason': 'Automated spam detection',
                'aspect': 'General'
            }
            
            # Fill template
            description = template['description_template'].format(**template_vars)
            
            # Add source information at the end
            source_section = f"\n\n---\nSource Information:\n"
            source_section += f"Source ID: {source_info.get('id', 'Unknown')}\n"
            source_section += f"Source Type: {source_info.get('source_type', 'Unknown')}\n"
            source_section += f"Timestamp: {source_info.get('timestamp', 'Unknown')}\n"
            if source_info.get('user_name'):
                source_section += f"User: {source_info.get('user_name', 'Anonymous')}\n"
            if source_info.get('sender_email'):
                source_section += f"Email: {source_info.get('sender_email', 'Not provided')}"
            
            description += source_section
            
            return description
            
        except Exception as e:
            self.logger.error(f"Error generating ticket description: {str(e)}")
            return f"Error generating description: {str(e)}\n\nOriginal Content:\n{content}"
    
    def _format_reproduction_steps(self, reproduction_steps: Dict) -> str:
        """Format reproduction steps for description"""
        steps = reproduction_steps.get('steps', [])
        if not steps:
            return "No specific steps provided"
        
        formatted_steps = []
        for i, step in enumerate(steps[:5], 1):  # Limit to 5 steps
            formatted_steps.append(f"{i}. {step}")
        
        return "\n".join(formatted_steps)
    
    def _extract_positive_points(self, content: str) -> str:
        """Extract positive points from content"""
        positive_words = ['love', 'great', 'amazing', 'excellent', 'perfect', 'awesome', 'fantastic']
        points = []
        
        sentences = content.split('.')
        for sentence in sentences:
            for word in positive_words:
                if word in sentence.lower():
                    points.append(sentence.strip())
                    break
        
        return "\n".join(points[:3]) if points else "General positive sentiment"
    
    def _extract_issue_type(self, content: str) -> str:
        """Extract issue type from complaint"""
        issue_keywords = {
            'price': 'Pricing Concern',
            'slow': 'Performance Issue',
            'service': 'Customer Service',
            'difficult': 'Usability Issue',
            'missing': 'Missing Feature',
            'expensive': 'Pricing Concern'
        }
        
        content_lower = content.lower()
        for keyword, issue_type in issue_keywords.items():
            if keyword in content_lower:
                return issue_type
        
        return "General Concern"
    
    def _extract_complaint_details(self, content: str) -> str:
        """Extract specific complaint details"""
        # Look for specific complaints
        complaint_patterns = [
            r'too\s+(?:expensive|costly)',
            r'slow\s+(?:performance|loading)',
            r'poor\s+(?:service|support)',
            r'can\'t\s+\w+',
            r'not\s+\w+ing',
            r'difficult\s+to\s+\w+'
        ]
        
        details = []
        for pattern in complaint_patterns:
            matches = re.findall(pattern, content.lower())
            details.extend(matches)
        
        return "; ".join(details) if details else "General complaint"
    
    def _generate_suggested_actions(self, category: str, analysis: Dict) -> str:
        """Generate suggested actions for the ticket"""
        if category == 'Bug':
            severity = analysis.get('severity_assessment', {}).get('severity', 'Medium')
            if severity == 'Critical':
                return "1. Immediate investigation required\n2. Prepare hotfix if needed\n3. Communicate with affected users"
            elif severity == 'High':
                return "1. Add to next sprint\n2. Investigate root cause\n3. Monitor for similar reports"
            else:
                return "1. Add to backlog\n2. Investigate when resources available"
        
        elif category == 'Feature Request':
            priority = analysis.get('priority_score', 0.5)
            if priority >= 0.8:
                return "1. Consider for immediate development\n2. Assess feasibility\n3. Create user story"
            elif priority >= 0.5:
                return "1. Add to product roadmap\n2. Gather more user feedback\n3. Evaluate ROI"
            else:
                return "1. Add to feature backlog\n2. Monitor for similar requests"
        
        elif category == 'Complaint':
            return "1. Investigate user concern\n2. Provide response to user\n3. Consider process improvements"
        
        elif category == 'Praise':
            return "1. Share positive feedback with team\n2. Consider highlighting in marketing\n3. No technical action needed"
        
        else:
            return "No action required"
    
    def determine_ticket_priority(self, category: str, analysis: Dict) -> str:
        """
        Determine ticket priority based on category and analysis
        
        Args:
            category (str): Feedback category
            analysis (Dict): Analysis results
            
        Returns:
            str: Ticket priority
        """
        try:
            if category == 'Bug':
                severity = analysis.get('severity_assessment', {}).get('severity', 'Medium')
                return self.priority_mapping['Bug'].get(severity, TicketPriority.MEDIUM.value)
            
            elif category == 'Feature Request':
                impact = analysis.get('impact_assessment', {}).get('impact_level', 'Medium')
                return self.priority_mapping['Feature Request'].get(impact, TicketPriority.MEDIUM.value)
            
            elif category == 'Complaint':
                impact = analysis.get('impact_assessment', {}).get('impact_level', 'Medium')
                return self.priority_mapping['Complaint'].get(impact, TicketPriority.MEDIUM.value)
            
            else:
                return TicketPriority.LOW.value
                
        except Exception as e:
            self.logger.error(f"Error determining ticket priority: {str(e)}")
            return TicketPriority.MEDIUM.value
    
    def create_ticket(self, feedback_data: Dict, analysis: Dict) -> Dict[str, Any]:
        """
        Create a structured ticket from feedback and analysis
        
        Args:
            feedback_data (Dict): Original feedback data
            analysis (Dict): Analysis results
            
        Returns:
            Dict[str, Any]: Created ticket
        """
        try:
            # Extract basic information
            category = analysis.get('category', feedback_data.get('predicted_category', 'Unknown'))
            content = feedback_data.get('content', feedback_data.get('review_text', feedback_data.get('body', '')))
            
            # Generate ticket components
            ticket_id = self.generate_ticket_id()
            title = self.generate_ticket_title(category, content, analysis)
            description = self.generate_ticket_description(category, content, analysis, feedback_data)
            priority = self.determine_ticket_priority(category, analysis)
            
            # Create ticket dictionary
            ticket = {
                'ticket_id': ticket_id,
                'title': title,
                'description': description,
                'category': category,
                'priority': priority,
                'status': TicketStatus.OPEN.value,
                'source_id': feedback_data.get('id', ''),
                'source_type': feedback_data.get('source_type', ''),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'assigned_to': '',
                'tags': ','.join(self.ticket_templates.get(category, {}).get('tags', [])),
                'classification_confidence': analysis.get('classification_confidence', 0.0),
                'analysis_summary': json.dumps(analysis)
            }
            
            self.logger.info(f"Created ticket {ticket_id} for {category} feedback")
            
            return ticket
            
        except Exception as e:
            self.logger.error(f"Error creating ticket: {str(e)}")
            # Create minimal ticket on error
            return {
                'ticket_id': self.generate_ticket_id(),
                'title': f"Error Processing: {feedback_data.get('id', 'Unknown')}",
                'description': f"Error creating ticket: {str(e)}\n\nOriginal content: {feedback_data.get('content', '')}",
                'category': 'Error',
                'priority': TicketPriority.MEDIUM.value,
                'status': TicketStatus.OPEN.value,
                'source_id': feedback_data.get('id', ''),
                'source_type': feedback_data.get('source_type', ''),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'assigned_to': '',
                'tags': 'error',
                'classification_confidence': 0.0,
                'analysis_summary': json.dumps({'error': str(e)})
            }
    
    def create_tickets_batch(self, feedback_data: pd.DataFrame, analysis_results: List[Dict]) -> List[Dict]:
        """
        Create tickets from a batch of feedback
        
        Args:
            feedback_data (pd.DataFrame): Feedback data
            analysis_results (List[Dict]): Analysis results for each feedback item
            
        Returns:
            List[Dict]: Created tickets
        """
        try:
            tickets = []
            
            for idx, (_, feedback_row) in enumerate(feedback_data.iterrows()):
                if idx < len(analysis_results):
                    feedback_dict = feedback_row.to_dict()
                    analysis = analysis_results[idx]
                    
                    ticket = self.create_ticket(feedback_dict, analysis)
                    tickets.append(ticket)
            
            self.logger.info(f"Created {len(tickets)} tickets from {len(feedback_data)} feedback items")
            
            return tickets
            
        except Exception as e:
            self.logger.error(f"Error creating tickets batch: {str(e)}")
            raise
    
    def save_tickets_to_csv(self, tickets: List[Dict]) -> str:
        """
        Save tickets to CSV file
        
        Args:
            tickets (List[Dict]): Tickets to save
            
        Returns:
            str: File path of saved CSV
        """
        try:
            if not tickets:
                self.logger.warning("No tickets to save")
                return self.tickets_file
            
            # Convert to DataFrame
            df = pd.DataFrame(tickets)
            
            # Define column order
            column_order = [
                'ticket_id', 'title', 'description', 'category', 'priority', 'status',
                'source_id', 'source_type', 'created_at', 'updated_at', 'assigned_to',
                'tags', 'classification_confidence'
            ]
            
            # Reorder columns
            df = df.reindex(columns=column_order + [col for col in df.columns if col not in column_order])
            
            # Save to CSV
            df.to_csv(self.tickets_file, index=False)
            
            self.logger.info(f"Saved {len(tickets)} tickets to {self.tickets_file}")
            
            return self.tickets_file
            
        except Exception as e:
            self.logger.error(f"Error saving tickets to CSV: {str(e)}")
            raise
    
    def log_processing_step(self, step: str, details: Dict, status: str = "Success"):
        """
        Log a processing step
        
        Args:
            step (str): Processing step name
            details (Dict): Step details
            status (str): Step status
        """
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'step': step,
                'status': status,
                'details': json.dumps(details)
            }
            
            # Create DataFrame and append to CSV
            log_df = pd.DataFrame([log_entry])
            
            # Check if file exists to determine if we need headers
            import os
            file_exists = os.path.exists(self.logs_file)
            
            # Append to CSV
            log_df.to_csv(self.logs_file, mode='a', header=not file_exists, index=False)
            
        except Exception as e:
            self.logger.error(f"Error logging processing step: {str(e)}")
    
    def get_ticket_stats(self, tickets: List[Dict]) -> Dict[str, Any]:
        """
        Get statistics about created tickets
        
        Args:
            tickets (List[Dict]): Created tickets
            
        Returns:
            Dict[str, Any]: Ticket statistics
        """
        try:
            if not tickets:
                return {'total_tickets': 0}
            
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(tickets)
            
            stats = {
                'total_tickets': len(tickets),
                'category_distribution': df['category'].value_counts().to_dict(),
                'priority_distribution': df['priority'].value_counts().to_dict(),
                'status_distribution': df['status'].value_counts().to_dict(),
                'source_type_distribution': df['source_type'].value_counts().to_dict(),
                'average_confidence': df['classification_confidence'].mean(),
                'tickets_by_date': df['created_at'].str[:10].value_counts().to_dict()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting ticket stats: {str(e)}")
            return {'error': str(e)}
