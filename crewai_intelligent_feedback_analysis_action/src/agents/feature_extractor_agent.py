"""
Feature Extractor Agent - Identifies feature requests and estimates user impact/demand
"""

import pandas as pd
import logging
import re
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import json
from collections import Counter
from crewai import Agent
from langchain_openai import ChatOpenAI

class FeatureCategory(Enum):
    """Feature request categories"""
    FUNCTIONALITY = "Functionality"
    UI_UX = "UI/UX"
    INTEGRATION = "Integration"
    PERFORMANCE = "Performance"
    SECURITY = "Security"
    ACCESSIBILITY = "Accessibility"
    AUTOMATION = "Automation"
    ANALYTICS = "Analytics"

class ImpactLevel(Enum):
    """User impact levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class FeatureExtractorAgent:
    """
    Agent responsible for analyzing feature requests and extracting:
    - Feature categories
    - User impact assessment
    - Demand estimation
    - Implementation complexity
    - Business value
    """
    
    def __init__(self):
        """Initialize the Feature Extractor Agent"""
        self.logger = logging.getLogger(__name__)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
        
        # Feature request patterns
        self.feature_patterns = [
            r'please\s+add',
            r'would\s+love\s+to\s+see',
            r'feature\s+request',
            r'suggestion',
            r'add\s+functionality',
            r'missing',
            r'would\s+be\s+nice',
            r'implement',
            r'new\s+feature',
            r'enhancement',
            r'improvement',
            r'wish',
            r'need\s+to\s+have',
            r'should\s+have',
            r'could\s+have',
            r'it\s+would\s+be\s+great\s+if',
            r'can\s+you\s+add',
            r'looking\s+for',
            r'hope\s+to\s+see'
        ]
        
        # Feature category patterns
        self.category_patterns = {
            FeatureCategory.FUNCTIONALITY.value: [
                r'add\s+\w+\s+feature',
                r'new\s+functionality',
                r'ability\s+to\s+\w+',
                r'option\s+to\s+\w+',
                r'allow\s+users?\s+to\s+\w+',
                r'enable\s+\w+',
                r'support\s+for\s+\w+',
                r'create\s+\w+',
                r'delete\s+\w+',
                r'edit\s+\w+',
                r'modify\s+\w+'
            ],
            FeatureCategory.UI_UX.value: [
                r'ui',
                r'interface',
                r'design',
                r'layout',
                r'dark\s+mode',
                r'theme',
                r'color',
                r'font',
                r'icon',
                r'button',
                r'menu',
                r'navigation',
                r'user\s+experience',
                r'ux',
                r'visual',
                r'appearance'
            ],
            FeatureCategory.INTEGRATION.value: [
                r'integration',
                r'connect\s+to',
                r'sync\s+with',
                r'link\s+to',
                r'api',
                r'export',
                r'import',
                r'share',
                r'calendar',
                r'email',
                r'drive',
                r'dropbox',
                r'slack',
                r'teams',
                r'zapier',
                r'webhook'
            ],
            FeatureCategory.PERFORMANCE.value: [
                r'faster',
                r'quick',
                r'speed',
                r'performance',
                r'optimize',
                r'cache',
                r'loading',
                r'response\s+time',
                r'lag',
                r'delay',
                r'efficient',
                r'resource'
            ],
            FeatureCategory.SECURITY.value: [
                r'security',
                r'authentication',
                r'login',
                r'password',
                r'2fa',
                r'two\s+factor',
                r'encryption',
                r'privacy',
                r'permission',
                r'access\s+control'
            ],
            FeatureCategory.ACCESSIBILITY.value: [
                r'accessibility',
                r'disability',
                r'screen\s+reader',
                r'keyboard',
                r'voice',
                r'high\s+contrast',
                r'large\s+text',
                r'color\s+blind',
                r'wcag',
                r'ada'
            ],
            FeatureCategory.AUTOMATION.value: [
                r'automation',
                r'auto',
                r'schedule',
                r'recurring',
                r'batch',
                r'bulk',
                r'template',
                r'workflow',
                r'trigger',
                r'rule'
            ],
            FeatureCategory.ANALYTICS.value: [
                r'analytics',
                r'report',
                r'statistics',
                r'metrics',
                r'dashboard',
                r'chart',
                r'graph',
                r'insights',
                r'tracking',
                r'monitoring'
            ]
        }
        
        # Impact indicators
        self.impact_indicators = {
            'critical': [
                r'can\'t\s+work\s+without',
                r'essential',
                r'must\s+have',
                r'critical',
                r'blocking',
                r'deal\s+breaker',
                r'unusable\s+without'
            ],
            'high': [
                r'very\s+important',
                r'high\s+priority',
                r'urgent',
                r'desperately\s+need',
                r'highly\s+requested',
                r'major\s+impact'
            ],
            'medium': [
                r'would\s+be\s+helpful',
                r'useful',
                r'would\s+improve',
                r'medium\s+priority',
                r'nice\s+to\s+have'
            ],
            'low': [
                r'minor',
                r'small\s+improvement',
                r'cosmetic',
                r'would\s+be\s+nice',
                r'low\s+priority',
                r'minor\s+detail'
            ]
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            'high': [
                r'completely\s+new',
                r'from\s+scratch',
                r'fundamental',
                r'architecture',
                r'backend',
                r'database',
                r'system\s+level'
            ],
            'medium': [
                r'add\s+to\s+existing',
                r'extend',
                r'enhance',
                r'improve',
                r'optimize'
            ],
            'low': [
                r'simple',
                r'easy',
                r'quick',
                r'minor',
                r'small',
                r'tweak',
                r'adjustment'
            ]
        }
        
        # Business value indicators
        self.business_value_indicators = {
            'high': [
                r'revenue',
                r'money',
                r'pay',
                r'business',
                r'enterprise',
                r'professional',
                r'commercial',
                r'market',
                r'competitive'
            ],
            'medium': [
                r'productivity',
                r'efficiency',
                r'time\s+saving',
                r'workflow',
                r'team',
                r'collaboration'
            ],
            'low': [
                r'convenience',
                r'personal',
                r'individual',
                r'preference',
                r'aesthetic'
            ]
        }
        
        # Create CrewAI agent
        self.agent = Agent(
            role="Feature Analysis Specialist",
            goal="Extract feature requests, assess user impact, and estimate demand for new features",
            backstory="You are an expert product analyst with deep experience in feature prioritization and user impact assessment.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def extract_feature_request(self, text: str) -> Dict[str, Any]:
        """
        Extract feature request details from text
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, Any]: Feature request extraction results
        """
        feature_info = {
            'is_feature_request': False,
            'confidence': 0.0,
            'feature_phrases': [],
            'patterns_matched': []
        }
        
        text_lower = text.lower()
        
        # Check for feature request patterns
        for pattern in self.feature_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                feature_info['is_feature_request'] = True
                feature_info['confidence'] += 0.2
                feature_info['patterns_matched'].append(pattern)
        
        # Extract feature phrases (what the user wants)
        feature_phrase_patterns = [
            r'please\s+add\s+([^.!?]+)',
            r'would\s+love\s+to\s+see\s+([^.!?]+)',
            r'add\s+([^.!?]+)\s+feature',
            r'ability\s+to\s+([^.!?]+)',
            r'option\s+to\s+([^.!?]+)',
            r'allow\s+(?:me|users?)\s+to\s+([^.!?]+)',
            r'enable\s+([^.!?]+)',
            r'support\s+for\s+([^.!?]+)',
            r'implement\s+([^.!?]+)',
            r'new\s+feature:\s*([^.!?]+)',
            r'feature:\s*([^.!?]+)',
            r'suggestion:\s*([^.!?]+)'
        ]
        
        for pattern in feature_phrase_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match.strip()) > 3:  # Filter out very short matches
                    feature_info['feature_phrases'].append(match.strip())
                    feature_info['confidence'] += 0.1
        
        # Normalize confidence
        feature_info['confidence'] = min(feature_info['confidence'], 1.0)
        
        return feature_info
    
    def categorize_feature(self, text: str) -> Dict[str, Any]:
        """
        Categorize feature request by type
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, Any]: Feature categorization
        """
        category_info = {
            'category': FeatureCategory.FUNCTIONALITY.value,
            'confidence': 0.0,
            'category_scores': {},
            'keywords_found': []
        }
        
        text_lower = text.lower()
        category_scores = {}
        
        # Score each category
        for category, patterns in self.category_patterns.items():
            score = 0
            keywords = []
            
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += len(matches)
                    keywords.extend(matches)
            
            category_scores[category] = score
            category_info['keywords_found'].extend(keywords)
        
        # Determine best category
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            best_score = category_scores[best_category]
            
            category_info['category'] = best_category
            category_info['category_scores'] = category_scores
            
            # Calculate confidence based on score difference
            if best_score > 0:
                total_score = sum(category_scores.values())
                category_info['confidence'] = best_score / total_score if total_score > 0 else 0.0
            else:
                category_info['confidence'] = 0.0
        else:
            category_info['category'] = FeatureCategory.FUNCTIONALITY.value
            category_info['confidence'] = 0.1
        
        # Remove duplicates and clean keywords
        category_info['keywords_found'] = list(set(category_info['keywords_found']))
        
        return category_info
    
    def assess_impact(self, text: str) -> Dict[str, Any]:
        """
        Assess user impact level
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, Any]: Impact assessment
        """
        impact_info = {
            'impact_level': ImpactLevel.MEDIUM.value,
            'confidence': 0.5,
            'factors': [],
            'score': 0.0
        }
        
        text_lower = text.lower()
        score = 0.0
        factors = []
        
        # Check for impact indicators
        for impact_level, patterns in self.impact_indicators.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if impact_level == 'critical':
                        score += 0.4
                        factors.append(f"Critical impact indicator: {pattern}")
                    elif impact_level == 'high':
                        score += 0.3
                        factors.append(f"High impact indicator: {pattern}")
                    elif impact_level == 'medium':
                        score += 0.2
                        factors.append(f"Medium impact indicator: {pattern}")
                    elif impact_level == 'low':
                        score += 0.1
                        factors.append(f"Low impact indicator: {pattern}")
        
        # Factor in language intensity
        intensity_words = ['very', 'extremely', 'really', 'absolutely', 'definitely', 'certainly']
        for word in intensity_words:
            if word in text_lower:
                score += 0.1
                factors.append(f"Intensity word: {word}")
        
        # Factor in frequency indicators
        frequency_words = ['always', 'never', 'constantly', 'continuously', 'repeatedly']
        for word in frequency_words:
            if word in text_lower:
                score += 0.1
                factors.append(f"Frequency indicator: {word}")
        
        # Factor in problem statement
        problem_words = ['problem', 'issue', 'difficulty', 'struggle', 'challenge', 'frustration']
        for word in problem_words:
            if word in text_lower:
                score += 0.1
                factors.append(f"Problem indicator: {word}")
        
        # Determine impact level based on score
        if score >= 0.8:
            impact_info['impact_level'] = ImpactLevel.CRITICAL.value
        elif score >= 0.6:
            impact_info['impact_level'] = ImpactLevel.HIGH.value
        elif score >= 0.3:
            impact_info['impact_level'] = ImpactLevel.MEDIUM.value
        else:
            impact_info['impact_level'] = ImpactLevel.LOW.value
        
        impact_info['score'] = score
        impact_info['confidence'] = min(score + 0.2, 1.0)
        impact_info['factors'] = factors
        
        return impact_info
    
    def estimate_complexity(self, text: str) -> Dict[str, Any]:
        """
        Estimate implementation complexity
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, Any]: Complexity estimation
        """
        complexity_info = {
            'complexity': 'Medium',
            'confidence': 0.5,
            'indicators': [],
            'score': 0.0
        }
        
        text_lower = text.lower()
        score = 0.0
        indicators = []
        
        # Check for complexity indicators
        for complexity, patterns in self.complexity_indicators.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if complexity == 'high':
                        score += 0.4
                        indicators.append(f"High complexity indicator: {pattern}")
                    elif complexity == 'medium':
                        score += 0.2
                        indicators.append(f"Medium complexity indicator: {pattern}")
                    elif complexity == 'low':
                        score += 0.1
                        indicators.append(f"Low complexity indicator: {pattern}")
        
        # Factor in technical terms
        technical_terms = ['api', 'database', 'backend', 'frontend', 'architecture', 'system', 'integration']
        for term in technical_terms:
            if term in text_lower:
                score += 0.1
                indicators.append(f"Technical term: {term}")
        
        # Determine complexity based on score
        if score >= 0.7:
            complexity_info['complexity'] = 'High'
        elif score >= 0.4:
            complexity_info['complexity'] = 'Medium'
        else:
            complexity_info['complexity'] = 'Low'
        
        complexity_info['score'] = score
        complexity_info['confidence'] = min(score + 0.3, 1.0)
        complexity_info['indicators'] = indicators
        
        return complexity_info
    
    def assess_business_value(self, text: str) -> Dict[str, Any]:
        """
        Assess business value of feature
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, Any]: Business value assessment
        """
        business_info = {
            'value': 'Medium',
            'confidence': 0.5,
            'indicators': [],
            'score': 0.0
        }
        
        text_lower = text.lower()
        score = 0.0
        indicators = []
        
        # Check for business value indicators
        for value, patterns in self.business_value_indicators.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if value == 'high':
                        score += 0.3
                        indicators.append(f"High value indicator: {pattern}")
                    elif value == 'medium':
                        score += 0.2
                        indicators.append(f"Medium value indicator: {pattern}")
                    elif value == 'low':
                        score += 0.1
                        indicators.append(f"Low value indicator: {pattern}")
        
        # Determine value based on score
        if score >= 0.6:
            business_info['value'] = 'High'
        elif score >= 0.3:
            business_info['value'] = 'Medium'
        else:
            business_info['value'] = 'Low'
        
        business_info['score'] = score
        business_info['confidence'] = min(score + 0.3, 1.0)
        business_info['indicators'] = indicators
        
        return business_info
    
    def analyze_feature_request(self, text: str, source_info: Dict = None) -> Dict[str, Any]:
        """
        Analyze a single feature request
        
        Args:
            text (str): Feature request text
            source_info (Dict): Additional source information
            
        Returns:
            Dict[str, Any]: Complete feature analysis
        """
        try:
            # Extract different aspects
            feature_extraction = self.extract_feature_request(text)
            category_info = self.categorize_feature(text)
            impact_info = self.assess_impact(text)
            complexity_info = self.estimate_complexity(text)
            business_info = self.assess_business_value(text)
            
            # Combine all information
            analysis = {
                'feature_extraction': feature_extraction,
                'category_info': category_info,
                'impact_assessment': impact_info,
                'complexity_estimation': complexity_info,
                'business_value': business_info,
                'feature_summary': self._generate_feature_summary(feature_extraction, category_info),
                'priority_score': self._calculate_priority_score(impact_info, complexity_info, business_info),
                'overall_confidence': (feature_extraction['confidence'] + category_info['confidence'] + 
                                    impact_info['confidence'] + complexity_info['confidence'] + 
                                    business_info['confidence']) / 5
            }
            
            # Add source information if provided
            if source_info:
                analysis['source_info'] = source_info
            
            self.logger.info(f"Feature analysis completed for category: {category_info['category']}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing feature request: {str(e)}")
            return {
                'feature_extraction': {'is_feature_request': False, 'confidence': 0.0},
                'category_info': {'category': FeatureCategory.FUNCTIONALITY.value, 'confidence': 0.0},
                'impact_assessment': {'impact_level': ImpactLevel.MEDIUM.value, 'confidence': 0.1},
                'complexity_estimation': {'complexity': 'Medium', 'confidence': 0.1},
                'business_value': {'value': 'Medium', 'confidence': 0.1},
                'feature_summary': 'Analysis failed due to error',
                'priority_score': 0.0,
                'overall_confidence': 0.1,
                'error': str(e)
            }
    
    def _generate_feature_summary(self, feature_extraction: Dict, category_info: Dict) -> str:
        """
        Generate feature summary
        
        Args:
            feature_extraction (Dict): Feature extraction results
            category_info (Dict): Category information
            
        Returns:
            str: Feature summary
        """
        if not feature_extraction['feature_phrases']:
            return "No clear feature request identified"
        
        feature_list = feature_extraction['feature_phrases'][:3]  # Limit to first 3
        category = category_info['category']
        
        summary = f"Feature request for {category.lower()}: "
        summary += "; ".join(feature_list)
        
        return summary
    
    def _calculate_priority_score(self, impact_info: Dict, complexity_info: Dict, business_info: Dict) -> float:
        """
        Calculate priority score based on impact, complexity, and business value
        
        Args:
            impact_info (Dict): Impact assessment
            config_info (Dict): Complexity estimation
            business_info (Dict): Business value assessment
            
        Returns:
            float: Priority score (0-1)
        """
        # Map levels to scores
        impact_scores = {'Critical': 1.0, 'High': 0.8, 'Medium': 0.5, 'Low': 0.2}
        complexity_scores = {'Low': 1.0, 'Medium': 0.6, 'High': 0.3}  # Lower complexity = higher score
        business_scores = {'High': 1.0, 'Medium': 0.6, 'Low': 0.2}
        
        impact_score = impact_scores.get(impact_info['impact_level'], 0.5)
        complexity_score = complexity_scores.get(complexity_info['complexity'], 0.6)
        business_score = business_scores.get(business_info['value'], 0.5)
        
        # Weighted average (impact is most important)
        priority_score = (impact_score * 0.5 + business_score * 0.3 + complexity_score * 0.2)
        
        return round(priority_score, 2)
    
    def analyze_batch(self, feature_requests: pd.DataFrame, text_column: str = 'content') -> pd.DataFrame:
        """
        Analyze a batch of feature requests
        
        Args:
            feature_requests (pd.DataFrame): Feature requests data
            text_column (str): Column name containing text
            
        Returns:
            pd.DataFrame: Data with feature analysis results
        """
        try:
            results = []
            
            for idx, row in feature_requests.iterrows():
                text = row[text_column]
                source_info = {
                    'source_id': row.get('id', ''),
                    'source_type': row.get('source_type', ''),
                    'timestamp': row.get('timestamp', '')
                }
                
                analysis = self.analyze_feature_request(text, source_info)
                
                # Add analysis results to row
                result_row = row.copy()
                result_row['feature_analysis'] = json.dumps(analysis)
                result_row['feature_category'] = analysis['category_info']['category']
                result_row['feature_impact'] = analysis['impact_assessment']['impact_level']
                result_row['feature_complexity'] = analysis['complexity_estimation']['complexity']
                result_row['feature_business_value'] = analysis['business_value']['value']
                result_row['feature_priority_score'] = analysis['priority_score']
                result_row['feature_summary'] = analysis['feature_summary']
                
                results.append(result_row)
            
            analyzed_df = pd.DataFrame(results)
            
            self.logger.info(f"Analyzed {len(analyzed_df)} feature requests")
            self.logger.info(f"Category distribution: {analyzed_df['feature_category'].value_counts().to_dict()}")
            
            return analyzed_df
            
        except Exception as e:
            self.logger.error(f"Error in batch feature analysis: {str(e)}")
            raise
    
    def get_feature_analysis_stats(self, analyzed_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get feature analysis statistics
        
        Args:
            analyzed_data (pd.DataFrame): Analyzed feature data
            
        Returns:
            Dict[str, Any]: Feature analysis statistics
        """
        try:
            stats = {
                'total_analyzed': len(analyzed_data),
                'category_distribution': analyzed_data['feature_category'].value_counts().to_dict(),
                'impact_distribution': analyzed_data['feature_impact'].value_counts().to_dict(),
                'complexity_distribution': analyzed_data['feature_complexity'].value_counts().to_dict(),
                'business_value_distribution': analyzed_data['feature_business_value'].value_counts().to_dict(),
                'priority_score_stats': {
                    'mean': analyzed_data['feature_priority_score'].mean(),
                    'median': analyzed_data['feature_priority_score'].median(),
                    'min': analyzed_data['feature_priority_score'].min(),
                    'max': analyzed_data['feature_priority_score'].max()
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting feature analysis stats: {str(e)}")
            raise
