"""
Quality Critic Agent - Reviews generated tickets for completeness and accuracy
"""

import pandas as pd
import logging
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from crewai import Agent
from langchain_openai import ChatOpenAI

class QualityScore(Enum):
    """Quality score levels"""
    EXCELLENT = "Excellent"
    GOOD = "Good"
    ACCEPTABLE = "Acceptable"
    NEEDS_IMPROVEMENT = "Needs Improvement"
    POOR = "Poor"

class QualityIssueType(Enum):
    """Types of quality issues"""
    MISSING_INFO = "Missing Information"
    UNCLEAR_TITLE = "Unclear Title"
    LOW_CONFIDENCE = "Low Confidence"
    INCORRECT_CATEGORY = "Incorrect Category"
    POOR_DESCRIPTION = "Poor Description"
    WRONG_PRIORITY = "Wrong Priority"
    INCOMPLETE_ANALYSIS = "Incomplete Analysis"

class QualityCriticAgent:
    """
    Agent responsible for reviewing and validating generated tickets:
    - Checks ticket completeness
    - Validates classification accuracy
    - Assesses description quality
    - Reviews priority assignment
    - Provides improvement suggestions
    """
    
    def __init__(self, min_confidence_threshold: float = 0.6):
        """
        Initialize the Quality Critic Agent
        
        Args:
            min_confidence_threshold (float): Minimum acceptable confidence score
        """
        self.min_confidence_threshold = min_confidence_threshold
        self.logger = logging.getLogger(__name__)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
        
        # Quality criteria weights
        self.quality_weights = {
            'title_quality': 0.2,
            'description_quality': 0.25,
            'classification_confidence': 0.2,
            'priority_appropriateness': 0.15,
            'completeness': 0.1,
            'technical_accuracy': 0.1
        }
        
        # Title quality indicators
        self.title_quality_patterns = {
            'good': [
                r'^(Bug|Feature Request|Positive|Complaint):\s+\w+',
                r'^\w+:\s+[A-Z][a-z]',
                r'.{20,80}$'  # Reasonable length
            ],
            'poor': [
                r'^General\s+Feedback',
                r'^Error\s+Processing',
                r'^.{1,10}$',  # Too short
                r'^.{100,}$'   # Too long
            ]
        }
        
        # Description quality indicators
        self.description_quality_patterns = {
            'good': [
                r'.{100,}',  # Minimum length
                r'(Platform|Device|Version|Steps|Details):',
                r'\d+\.\s+',  # Numbered lists
                r'(Description|Summary|Technical):'
            ],
            'poor': [
                r'^.{1,50}$',  # Too short
                r'Error\s+generating',
                r'No\s+specific\s+steps',
                r'Not\s+provided'
            ]
        }
        
        # Priority appropriateness checks
        self.priority_rules = {
            'Bug': {
                'Critical': ['crash', 'data loss', 'security', 'unusable', 'critical'],
                'High': ['freeze', 'login', 'sync', 'can\'t', 'broken'],
                'Medium': ['slow', 'performance', 'lag', 'annoying'],
                'Low': ['minor', 'cosmetic', 'typo', 'small']
            },
            'Feature Request': {
                'Critical': [],  # Features rarely critical
                'High': ['essential', 'must have', 'critical', 'blocking'],
                'Medium': ['useful', 'helpful', 'improve', 'enhance'],
                'Low': ['nice to have', 'minor', 'cosmetic']
            }
        }
        
        # Create CrewAI agent
        self.agent = Agent(
            role="Quality Assurance Specialist",
            goal="Review and validate generated tickets for completeness, accuracy, and quality",
            backstory="You are an expert quality assurance specialist with deep experience in technical support and ticket validation.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def assess_title_quality(self, ticket: Dict) -> Dict[str, Any]:
        """
        Assess the quality of ticket title
        
        Args:
            ticket (Dict): Ticket data
            
        Returns:
            Dict[str, Any]: Title quality assessment
        """
        title = ticket.get('title', '')
        category = ticket.get('category', '')
        
        assessment = {
            'score': 0.0,
            'issues': [],
            'suggestions': []
        }
        
        # Check title length
        if len(title) < 10:
            assessment['score'] -= 0.3
            assessment['issues'].append('Title too short')
            assessment['suggestions'].append('Add more specific details to title')
        elif len(title) > 100:
            assessment['score'] -= 0.2
            assessment['issues'].append('Title too long')
            assessment['suggestions'].append('Shorten title while keeping key information')
        else:
            assessment['score'] += 0.3
        
        # Check title format
        if re.match(r'^(Bug|Feature Request|Positive|Complaint):', title):
            assessment['score'] += 0.4
        else:
            assessment['score'] -= 0.2
            assessment['issues'].append('Title format unclear')
            assessment['suggestions'].append('Start title with category (Bug:, Feature Request:, etc.)')
        
        # Check for specific information
        if category.lower() in title.lower():
            assessment['score'] += 0.2
        else:
            assessment['score'] -= 0.1
            assessment['issues'].append('Title doesn\'t clearly indicate category')
        
        # Check for generic titles
        generic_patterns = ['general feedback', 'error processing', 'user feedback']
        for pattern in generic_patterns:
            if pattern.lower() in title.lower():
                assessment['score'] -= 0.3
                assessment['issues'].append(f'Generic title: {pattern}')
                assessment['suggestions'].append('Make title more specific and actionable')
        
        # Normalize score
        assessment['score'] = max(0, min(1, assessment['score'] + 0.5))  # Base score of 0.5
        
        return assessment
    
    def assess_description_quality(self, ticket: Dict) -> Dict[str, Any]:
        """
        Assess the quality of ticket description
        
        Args:
            ticket (Dict): Ticket data
            
        Returns:
            Dict[str, Any]: Description quality assessment
        """
        description = ticket.get('description', '')
        category = ticket.get('category', '')
        
        assessment = {
            'score': 0.0,
            'issues': [],
            'suggestions': []
        }
        
        # Check description length
        if len(description) < 50:
            assessment['score'] -= 0.4
            assessment['issues'].append('Description too short')
            assessment['suggestions'].append('Add more details about the issue/request')
        elif len(description) < 150:
            assessment['score'] -= 0.2
            assessment['issues'].append('Description could be more detailed')
            assessment['suggestions'].append('Add specific examples or steps')
        else:
            assessment['score'] += 0.3
        
        # Check for structured information
        if 'Platform:' in description or 'Device:' in description:
            assessment['score'] += 0.2
        else:
            assessment['issues'].append('Missing platform/device information')
            assessment['suggestions'].append('Add platform and device details')
        
        # Check for technical details (for bugs)
        if category == 'Bug':
            if any(keyword in description.lower() for keyword in ['steps', 'reproduce', 'technical', 'error']):
                assessment['score'] += 0.3
            else:
                assessment['score'] -= 0.3
                assessment['issues'].append('Missing technical details or reproduction steps')
                assessment['suggestions'].append('Add steps to reproduce and technical details')
        
        # Check for feature details (for feature requests)
        if category == 'Feature Request':
            if any(keyword in description.lower() for keyword in ['feature', 'functionality', 'implementation', 'value']):
                assessment['score'] += 0.3
            else:
                assessment['score'] -= 0.2
                assessment['issues'].append('Missing feature details')
                assessment['suggestions'].append('Add specific feature requirements and expected benefits')
        
        # Check for error indicators
        error_indicators = ['error generating', 'failed due to error', 'not provided']
        for indicator in error_indicators:
            if indicator in description.lower():
                assessment['score'] -= 0.4
                assessment['issues'].append(f'Error in description: {indicator}')
                assessment['suggestions'].append('Fix description generation issues')
        
        # Normalize score
        assessment['score'] = max(0, min(1, assessment['score'] + 0.5))  # Base score of 0.5
        
        return assessment
    
    def assess_classification_confidence(self, ticket: Dict) -> Dict[str, Any]:
        """
        Assess classification confidence
        
        Args:
            ticket (Dict): Ticket data
            
        Returns:
            Dict[str, Any]: Classification confidence assessment
        """
        confidence = ticket.get('classification_confidence', 0.0)
        category = ticket.get('category', '')
        
        assessment = {
            'score': 0.0,
            'issues': [],
            'suggestions': []
        }
        
        # Base score from confidence value
        assessment['score'] = confidence
        
        if confidence < self.min_confidence_threshold:
            assessment['issues'].append(f'Low classification confidence: {confidence:.2f}')
            assessment['suggestions'].append('Review classification manually')
            assessment['score'] -= 0.2
        elif confidence > 0.9:
            assessment['score'] += 0.1
        
        # Check for consistency between category and content
        description = ticket.get('description', '').lower()
        title = ticket.get('title', '').lower()
        content = description + ' ' + title
        
        # Category-specific consistency checks
        if category == 'Bug':
            bug_indicators = ['bug', 'crash', 'error', 'issue', 'problem', 'broken']
            if not any(indicator in content for indicator in bug_indicators):
                assessment['issues'].append('Category may not match content (Bug)')
                assessment['suggestions'].append('Review if this is actually a bug report')
                assessment['score'] -= 0.2
            else:
                assessment['score'] += 0.1
        
        elif category == 'Feature Request':
            feature_indicators = ['feature', 'request', 'add', 'implement', 'suggestion']
            if not any(indicator in content for indicator in feature_indicators):
                assessment['issues'].append('Category may not match content (Feature Request)')
                assessment['suggestions'].append('Review if this is actually a feature request')
                assessment['score'] -= 0.2
            else:
                assessment['score'] += 0.1
        
        # Normalize score
        assessment['score'] = max(0, min(1, assessment['score']))
        
        return assessment
    
    def assess_priority_appropriateness(self, ticket: Dict) -> Dict[str, Any]:
        """
        Assess if priority is appropriate for the ticket
        
        Args:
            ticket (Dict): Ticket data
            
        Returns:
            Dict[str, Any]: Priority appropriateness assessment
        """
        priority = ticket.get('priority', '')
        category = ticket.get('category', '')
        description = ticket.get('description', '').lower()
        title = ticket.get('title', '').lower()
        content = description + ' ' + title
        
        assessment = {
            'score': 0.5,  # Start with neutral score
            'issues': [],
            'suggestions': []
        }
        
        # Check priority rules for category
        if category in self.priority_rules:
            category_rules = self.priority_rules[category]
            
            if priority in category_rules:
                # Check if content matches priority indicators
                indicators = category_rules[priority]
                
                if indicators:  # If there are specific indicators
                    if any(indicator in content for indicator in indicators):
                        assessment['score'] += 0.3
                    else:
                        assessment['score'] -= 0.2
                        assessment['issues'].append(f'Priority {priority} may not match content')
                        assessment['suggestions'].append('Review priority assignment')
                else:
                    # For priorities without specific indicators (like Critical for features)
                    if priority == 'Critical' and category == 'Feature Request':
                        assessment['score'] -= 0.3
                        assessment['issues'].append('Feature requests should rarely be Critical')
                        assessment['suggestions'].append('Consider lowering priority to High or Medium')
            else:
                assessment['issues'].append(f'Unexpected priority {priority} for category {category}')
                assessment['suggestions'].append('Review priority assignment')
                assessment['score'] -= 0.2
        
        # Special checks for Critical priority
        if priority == 'Critical':
            critical_indicators = ['data loss', 'security', 'crash', 'unusable', 'blocking']
            if not any(indicator in content for indicator in critical_indicators):
                assessment['score'] -= 0.3
                assessment['issues'].append('Critical priority without critical indicators')
                assessment['suggestions'].append('Review if this truly requires Critical priority')
        
        # Special checks for Low priority
        if priority == 'Low':
            if category == 'Bug':
                assessment['score'] -= 0.2
                assessment['issues'].append('Bugs should rarely be Low priority')
                assessment['suggestions'].append('Consider raising priority to at least Medium')
        
        # Normalize score
        assessment['score'] = max(0, min(1, assessment['score']))
        
        return assessment
    
    def assess_completeness(self, ticket: Dict) -> Dict[str, Any]:
        """
        Assess ticket completeness
        
        Args:
            ticket (Dict): Ticket data
            
        Returns:
            Dict[str, Any]: Completeness assessment
        """
        assessment = {
            'score': 0.5,  # Start with neutral score
            'issues': [],
            'suggestions': []
        }
        
        required_fields = ['ticket_id', 'title', 'description', 'category', 'priority', 'status']
        missing_fields = []
        
        for field in required_fields:
            if not ticket.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            assessment['score'] -= 0.3 * len(missing_fields)
            assessment['issues'].append(f'Missing required fields: {", ".join(missing_fields)}')
            assessment['suggestions'].append('Complete all required ticket fields')
        else:
            assessment['score'] += 0.2
        
        # Check for source information
        if not ticket.get('source_id'):
            assessment['issues'].append('Missing source ID')
            assessment['suggestions'].append('Add source ID for traceability')
            assessment['score'] -= 0.1
        else:
            assessment['score'] += 0.1
        
        # Check for timestamps
        if not ticket.get('created_at'):
            assessment['issues'].append('Missing creation timestamp')
            assessment['suggestions'].append('Add creation timestamp')
            assessment['score'] -= 0.1
        else:
            assessment['score'] += 0.1
        
        # Check for tags
        if not ticket.get('tags'):
            assessment['issues'].append('Missing tags')
            assessment['suggestions'].append('Add relevant tags for better organization')
            assessment['score'] -= 0.1
        else:
            assessment['score'] += 0.1
        
        # Normalize score
        assessment['score'] = max(0, min(1, assessment['score']))
        
        return assessment
    
    def assess_technical_accuracy(self, ticket: Dict) -> Dict[str, Any]:
        """
        Assess technical accuracy of the ticket
        
        Args:
            ticket (Dict): Ticket data
            
        Returns:
            Dict[str, Any]: Technical accuracy assessment
        """
        description = ticket.get('description', '')
        category = ticket.get('category', '')
        
        assessment = {
            'score': 0.5,  # Start with neutral score
            'issues': [],
            'suggestions': []
        }
        
        # Check for technical consistency
        if category == 'Bug':
            # Check for version information
            if 'Version:' in description or 'version' in description.lower():
                assessment['score'] += 0.2
            else:
                assessment['issues'].append('Missing version information')
                assessment['suggestions'].append('Add app version details')
                assessment['score'] -= 0.1
            
            # Check for platform/device info
            if 'Platform:' in description or 'Device:' in description:
                assessment['score'] += 0.2
            else:
                assessment['issues'].append('Missing platform/device information')
                assessment['suggestions'].append('Add platform and device details')
                assessment['score'] -= 0.1
        
        # Check for error messages
        error_indicators = ['Error:', 'Exception:', 'Failed:', 'Cannot']
        if any(indicator in description for indicator in error_indicators):
            assessment['score'] += 0.1
        
        # Check for clear problem statement
        if description.count('.') >= 2:  # At least 2 sentences
            assessment['score'] += 0.1
        else:
            assessment['issues'].append('Description too brief')
            assessment['suggestions'].append('Add more detailed problem description')
            assessment['score'] -= 0.1
        
        # Normalize score
        assessment['score'] = max(0, min(1, assessment['score']))
        
        return assessment
    
    def review_ticket(self, ticket: Dict) -> Dict[str, Any]:
        """
        Review a single ticket for quality
        
        Args:
            ticket (Dict): Ticket to review
            
        Returns:
            Dict[str, Any]: Quality review results
        """
        try:
            # Assess different aspects
            title_assessment = self.assess_title_quality(ticket)
            description_assessment = self.assess_description_quality(ticket)
            confidence_assessment = self.assess_classification_confidence(ticket)
            priority_assessment = self.assess_priority_appropriateness(ticket)
            completeness_assessment = self.assess_completeness(ticket)
            technical_assessment = self.assess_technical_accuracy(ticket)
            
            # Calculate weighted overall score
            overall_score = (
                title_assessment['score'] * self.quality_weights['title_quality'] +
                description_assessment['score'] * self.quality_weights['description_quality'] +
                confidence_assessment['score'] * self.quality_weights['classification_confidence'] +
                priority_assessment['score'] * self.quality_weights['priority_appropriateness'] +
                completeness_assessment['score'] * self.quality_weights['completeness'] +
                technical_assessment['score'] * self.quality_weights['technical_accuracy']
            )
            
            # Determine quality level
            if overall_score >= 0.9:
                quality_level = QualityScore.EXCELLENT.value
            elif overall_score >= 0.8:
                quality_level = QualityScore.GOOD.value
            elif overall_score >= 0.7:
                quality_level = QualityScore.ACCEPTABLE.value
            elif overall_score >= 0.6:
                quality_level = QualityScore.NEEDS_IMPROVEMENT.value
            else:
                quality_level = QualityScore.POOR.value
            
            # Collect all issues and suggestions
            all_issues = []
            all_suggestions = []
            
            for assessment in [title_assessment, description_assessment, confidence_assessment, 
                             priority_assessment, completeness_assessment, technical_assessment]:
                all_issues.extend(assessment['issues'])
                all_suggestions.extend(assessment['suggestions'])
            
            # Create review result
            review_result = {
                'ticket_id': ticket.get('ticket_id', ''),
                'overall_score': round(overall_score, 3),
                'quality_level': quality_level,
                'assessments': {
                    'title_quality': title_assessment,
                    'description_quality': description_assessment,
                    'classification_confidence': confidence_assessment,
                    'priority_appropriateness': priority_assessment,
                    'completeness': completeness_assessment,
                    'technical_accuracy': technical_assessment
                },
                'issues': all_issues,
                'suggestions': all_suggestions,
                'needs_manual_review': overall_score < 0.7,
                'review_timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Reviewed ticket {ticket.get('ticket_id')}: {quality_level} ({overall_score:.3f})")
            
            return review_result
            
        except Exception as e:
            self.logger.error(f"Error reviewing ticket: {str(e)}")
            return {
                'ticket_id': ticket.get('ticket_id', ''),
                'overall_score': 0.0,
                'quality_level': QualityScore.POOR.value,
                'error': str(e),
                'needs_manual_review': True,
                'review_timestamp': datetime.now().isoformat()
            }
    
    def review_tickets_batch(self, tickets: List[Dict]) -> List[Dict]:
        """
        Review a batch of tickets
        
        Args:
            tickets (List[Dict]): Tickets to review
            
        Returns:
            List[Dict]: Review results for all tickets
        """
        try:
            reviews = []
            
            for ticket in tickets:
                review = self.review_ticket(ticket)
                reviews.append(review)
            
            self.logger.info(f"Reviewed {len(reviews)} tickets")
            
            return reviews
            
        except Exception as e:
            self.logger.error(f"Error reviewing tickets batch: {str(e)}")
            raise
    
    def get_quality_stats(self, reviews: List[Dict]) -> Dict[str, Any]:
        """
        Get quality statistics from reviews
        
        Args:
            reviews (List[Dict]): Review results
            
        Returns:
            Dict[str, Any]: Quality statistics
        """
        try:
            if not reviews:
                return {'total_reviews': 0}
            
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(reviews)
            
            stats = {
                'total_reviews': len(reviews),
                'quality_level_distribution': df['quality_level'].value_counts().to_dict(),
                'average_score': df['overall_score'].mean(),
                'median_score': df['overall_score'].median(),
                'min_score': df['overall_score'].min(),
                'max_score': df['overall_score'].max(),
                'tickets_need_review': df['needs_manual_review'].sum(),
                'common_issues': self._get_common_issues(reviews),
                'assessment_scores': {
                    'title_quality': df['assessments'].apply(lambda x: x['title_quality']['score']).mean(),
                    'description_quality': df['assessments'].apply(lambda x: x['description_quality']['score']).mean(),
                    'classification_confidence': df['assessments'].apply(lambda x: x['classification_confidence']['score']).mean(),
                    'priority_appropriateness': df['assessments'].apply(lambda x: x['priority_appropriateness']['score']).mean(),
                    'completeness': df['assessments'].apply(lambda x: x['completeness']['score']).mean(),
                    'technical_accuracy': df['assessments'].apply(lambda x: x['technical_accuracy']['score']).mean()
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting quality stats: {str(e)}")
            return {'error': str(e)}
    
    def _get_common_issues(self, reviews: List[Dict]) -> Dict[str, int]:
        """Get most common issues from reviews"""
        issue_counts = {}
        
        for review in reviews:
            for issue in review.get('issues', []):
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        # Sort by frequency and return top 10
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_issues[:10])
    
    def approve_ticket(self, ticket: Dict, review: Dict) -> Dict[str, Any]:
        """
        Approve a ticket after review
        
        Args:
            ticket (Dict): Original ticket
            review (Dict): Quality review
            
        Returns:
            Dict[str, Any]: Updated ticket with approval status
        """
        try:
            # Update ticket with review information
            updated_ticket = ticket.copy()
            updated_ticket['quality_score'] = review['overall_score']
            updated_ticket['quality_level'] = review['quality_level']
            updated_ticket['review_status'] = 'Approved'
            updated_ticket['review_timestamp'] = review['review_timestamp']
            updated_ticket['updated_at'] = datetime.now().isoformat()
            
            # Add suggestions as comments if there are any
            if review['suggestions']:
                updated_ticket['review_comments'] = '; '.join(review['suggestions'])
            
            return updated_ticket
            
        except Exception as e:
            self.logger.error(f"Error approving ticket: {str(e)}")
            return ticket
    
    def reject_ticket(self, ticket: Dict, review: Dict, reason: str = "") -> Dict[str, Any]:
        """
        Reject a ticket after review
        
        Args:
            ticket (Dict): Original ticket
            review (Dict): Quality review
            reason (str): Additional rejection reason
            
        Returns:
            Dict[str, Any]: Updated ticket with rejection status
        """
        try:
            # Update ticket with review information
            updated_ticket = ticket.copy()
            updated_ticket['quality_score'] = review['overall_score']
            updated_ticket['quality_level'] = review['quality_level']
            updated_ticket['review_status'] = 'Rejected'
            updated_ticket['rejection_reason'] = reason or '; '.join(review['issues'])
            updated_ticket['review_timestamp'] = review['review_timestamp']
            updated_ticket['updated_at'] = datetime.now().isoformat()
            
            return updated_ticket
            
        except Exception as e:
            self.logger.error(f"Error rejecting ticket: {str(e)}")
            return ticket
