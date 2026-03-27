"""
Bug Analysis Agent - Extracts technical details: steps to reproduce, platform info, severity assessment
"""

import pandas as pd
import logging
import re
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import json
from crewai import Agent
from langchain_openai import ChatOpenAI

class SeverityLevel(Enum):
    """Bug severity levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class BugAnalysisAgent:
    """
    Agent responsible for analyzing bug reports and extracting:
    - Technical details
    - Steps to reproduce
    - Platform information
    - Severity assessment
    - Device information
    - Error patterns
    """
    
    def __init__(self):
        """Initialize the Bug Analysis Agent"""
        self.logger = logging.getLogger(__name__)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
        
        # Platform and device patterns
        self.device_patterns = {
            'ios': [
                r'iphone\s*\d+(?:\s*pro)?(?:\s*max)?',
                r'ipad\s*(?:air|pro|mini)?\s*\d*',
                r'ios\s*\d+(?:\.\d+)*',
                r'ipad',
                r'iphone'
            ],
            'android': [
                r'android\s*\d+(?:\.\d+)*',
                r'samsung\s*galaxy\s*\w+\s*\d*',
                r'google\s*pixel\s*\d*',
                r'oneplus\s*\d+',
                r'huawei\s*\w+',
                r'xiaomi\s*\w+',
                r'motorola\s*\w+',
                r'lg\s*\w+',
                r'sony\s*\w+',
                r'htc\s*\w+'
            ],
            'web': [
                r'chrome',
                r'firefox',
                r'safari',
                r'edge',
                r'browser',
                r'web\s*app'
            ],
            'desktop': [
                r'windows\s*\d+(?:\.\d+)*',
                r'mac\s*os\s*\w+(?:\s*\d+)?',
                r'linux',
                r'ubuntu',
                r'desktop',
                r'pc'
            ]
        }
        
        # Error patterns
        self.error_patterns = [
            r'error\s*\d*',
            r'exception',
            r'crash',
            r'freeze',
            r'hang',
            r'timeout',
            r'connection\s*failed',
            r'authentication\s*failed',
            r'login\s*failed',
            r'data\s*loss',
            r'sync\s*failed',
            r'not\s*working',
            r'broken',
            r'bug',
            r'glitch',
            r'malfunction'
        ]
        
        # Severity indicators
        self.severity_indicators = {
            'critical': [
                r'data\s*loss',
                r'security',
                r'crash.*startup',
                r'bricked',
                r'unusable',
                r'complete\s*failure',
                r'system\s*failure',
                r'critical'
            ],
            'high': [
                r'crash',
                r'freeze',
                r'login\s*issue',
                r'sync\s*issue',
                r'can\'t\s*login',
                r'can\'t\s*access',
                r'major\s*problem',
                r'urgent',
                r'high\s*priority'
            ],
            'medium': [
                r'slow',
                r'performance',
                r'lag',
                r'delay',
                r'annoying',
                r'frustrating',
                r'medium\s*priority'
            ],
            'low': [
                r'minor',
                r'small\s*issue',
                r'cosmetic',
                r'typo',
                r'suggestion',
                r'low\s*priority'
            ]
        }
        
        # Step reproduction patterns
        self.step_patterns = [
            r'steps?\s*to\s*reproduce',
            r'how\s*to\s*reproduce',
            r'reproduction\s*steps?',
            r'when\s*i\s*\w+',
            r'after\s*i\s*\w+',
            r'first\s*i\s*\w+',
            r'then\s*i\s*\w+',
            r'next\s*i\s*\w+',
            r'finally\s*i\s*\w+',
            r'1\.',
            r'2\.',
            r'3\.',
            r'first,',
            r'second,',
            r'third,'
        ]
        
        # Create CrewAI agent
        self.agent = Agent(
            role="Bug Analysis Specialist",
            goal="Extract technical details, reproduction steps, and assess bug severity from user reports",
            backstory="You are an expert technical analyst with deep experience in software debugging and bug triage.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def extract_platform_info(self, text: str) -> Dict[str, Any]:
        """
        Extract platform and device information from text
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, Any]: Platform information
        """
        platform_info = {
            'platform': 'Unknown',
            'devices': [],
            'os_versions': [],
            'app_versions': [],
            'confidence': 0.0
        }
        
        text_lower = text.lower()
        
        # Check for iOS devices
        for pattern in self.device_patterns['ios']:
            matches = re.findall(pattern, text_lower)
            if matches:
                platform_info['platform'] = 'iOS'
                platform_info['devices'].extend(matches)
                platform_info['confidence'] += 0.3
        
        # Check for Android devices
        for pattern in self.device_patterns['android']:
            matches = re.findall(pattern, text_lower)
            if matches:
                platform_info['platform'] = 'Android'
                platform_info['devices'].extend(matches)
                platform_info['confidence'] += 0.3
        
        # Check for web/desktop
        for pattern in self.device_patterns['web']:
            if re.search(pattern, text_lower):
                platform_info['platform'] = 'Web'
                platform_info['confidence'] += 0.2
        
        for pattern in self.device_patterns['desktop']:
            if re.search(pattern, text_lower):
                if platform_info['platform'] == 'Unknown':
                    platform_info['platform'] = 'Desktop'
                platform_info['confidence'] += 0.2
        
        # Extract OS versions
        os_version_patterns = [
            r'ios\s*(\d+(?:\.\d+)*)',
            r'android\s*(\d+(?:\.\d+)*)',
            r'windows\s*(\d+(?:\.\d+)*)',
            r'mac\s*os\s*(\w+(?:\s*\d+)?)'
        ]
        
        for pattern in os_version_patterns:
            matches = re.findall(pattern, text_lower)
            platform_info['os_versions'].extend(matches)
        
        # Extract app versions
        app_version_patterns = [
            r'version\s*(\d+(?:\.\d+)*)',
            r'v(\d+(?:\.\d+)*)',
            r'app\s*version\s*(\d+(?:\.\d+)*)'
        ]
        
        for pattern in app_version_patterns:
            matches = re.findall(pattern, text_lower)
            platform_info['app_versions'].extend(matches)
        
        # Normalize confidence
        platform_info['confidence'] = min(platform_info['confidence'], 1.0)
        
        return platform_info
    
    def extract_error_patterns(self, text: str) -> Dict[str, Any]:
        """
        Extract error patterns and types
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, Any]: Error information
        """
        error_info = {
            'error_types': [],
            'error_messages': [],
            'error_context': [],
            'confidence': 0.0
        }
        
        text_lower = text.lower()
        
        # Find error types
        for pattern in self.error_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                error_info['error_types'].extend(matches)
                error_info['confidence'] += 0.2
        
        # Extract specific error messages (in quotes or after "error:")
        error_message_patterns = [
            r'error[:\s]*["\']([^"\']+)["\']',
            r'error[:\s]*([^.!?\n]+)',
            r'exception[:\s]*["\']([^"\']+)["\']',
            r'failed[:\s]*([^.!?\n]+)'
        ]
        
        for pattern in error_message_patterns:
            matches = re.findall(pattern, text_lower)
            error_info['error_messages'].extend(matches)
        
        # Extract context around errors
        context_patterns = [
            r'when\s+i\s+\w+[^.!?]*',
            r'after\s+i\s+\w+[^.!?]*',
            r'during\s+\w+[^.!?]*'
        ]
        
        for pattern in context_patterns:
            matches = re.findall(pattern, text_lower)
            error_info['error_context'].extend(matches)
        
        # Remove duplicates and normalize
        error_info['error_types'] = list(set(error_info['error_types']))
        error_info['error_messages'] = list(set(error_info['error_messages']))
        error_info['error_context'] = list(set(error_info['error_context']))
        
        # Normalize confidence
        error_info['confidence'] = min(error_info['confidence'], 1.0)
        
        return error_info
    
    def extract_reproduction_steps(self, text: str) -> Dict[str, Any]:
        """
        Extract steps to reproduce the bug
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, Any]: Reproduction steps
        """
        steps_info = {
            'steps': [],
            'has_numbered_steps': False,
            'has_sequential_language': False,
            'confidence': 0.0
        }
        
        text_lower = text.lower()
        
        # Check for numbered steps
        numbered_steps = re.findall(r'\d+\.\s*([^.!?]+)', text_lower)
        if numbered_steps:
            steps_info['steps'] = numbered_steps
            steps_info['has_numbered_steps'] = True
            steps_info['confidence'] += 0.5
        
        # Check for sequential language
        sequential_patterns = [
            r'first\s+i\s+([^.!?]+)',
            r'then\s+i\s+([^.!?]+)',
            r'next\s+i\s+([^.!?]+)',
            r'after\s+i\s+([^.!?]+)',
            r'finally\s+i\s+([^.!?]+)'
        ]
        
        for pattern in sequential_patterns:
            matches = re.findall(pattern, text_lower)
            steps_info['steps'].extend(matches)
            if matches:
                steps_info['has_sequential_language'] = True
                steps_info['confidence'] += 0.3
        
        # Check for step indicators
        for pattern in self.step_patterns:
            if re.search(pattern, text_lower):
                steps_info['confidence'] += 0.2
                break
        
        # Extract sentences with action verbs
        action_patterns = [
            r'i\s+(open|click|tap|press|navigate|try|attempt|go|select)[^.!?]*',
            r'when\s+i\s+(open|click|tap|press|navigate|try|attempt|go|select)[^.!?]*',
            r'(open|click|tap|press|navigate|try|attempt|go|select)\s+the\s+[^.!?]*'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    steps_info['steps'].append(match[0] if match[0] else match[1])
                else:
                    steps_info['steps'].append(match)
        
        # Clean and deduplicate steps
        steps_info['steps'] = list(set([step.strip() for step in steps_info['steps'] if step.strip()]))
        
        # Normalize confidence
        steps_info['confidence'] = min(steps_info['confidence'], 1.0)
        
        return steps_info
    
    def assess_severity(self, text: str, platform_info: Dict, error_info: Dict, steps_info: Dict) -> Dict[str, Any]:
        """
        Assess bug severity based on multiple factors
        
        Args:
            text (str): Input text
            platform_info (Dict): Platform information
            error_info (Dict): Error information
            steps_info (Dict): Reproduction steps
            
        Returns:
            Dict[str, Any]: Severity assessment
        """
        severity_info = {
            'severity': SeverityLevel.MEDIUM.value,
            'confidence': 0.5,
            'factors': [],
            'score': 0.0
        }
        
        text_lower = text.lower()
        score = 0.0
        factors = []
        
        # Check for severity indicators
        for severity, patterns in self.severity_indicators.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if severity == 'critical':
                        score += 0.4
                        factors.append(f"Critical indicator: {pattern}")
                    elif severity == 'high':
                        score += 0.3
                        factors.append(f"High severity indicator: {pattern}")
                    elif severity == 'medium':
                        score += 0.2
                        factors.append(f"Medium severity indicator: {pattern}")
                    elif severity == 'low':
                        score += 0.1
                        factors.append(f"Low severity indicator: {pattern}")
        
        # Factor in error types
        critical_errors = ['crash', 'freeze', 'data loss', 'security']
        for error_type in error_info['error_types']:
            if error_type in critical_errors:
                score += 0.3
                factors.append(f"Critical error type: {error_type}")
        
        # Factor in reproducibility
        if steps_info['has_numbered_steps']:
            score += 0.2
            factors.append("Clear reproduction steps provided")
        elif steps_info['has_sequential_language']:
            score += 0.1
            factors.append("Sequential reproduction steps")
        
        # Factor in platform info confidence
        if platform_info['confidence'] > 0.7:
            score += 0.1
            factors.append("Detailed platform information")
        
        # Factor in text length and detail
        if len(text.split()) > 50:
            score += 0.1
            factors.append("Detailed bug report")
        
        # Determine severity based on score
        if score >= 0.8:
            severity_info['severity'] = SeverityLevel.CRITICAL.value
        elif score >= 0.6:
            severity_info['severity'] = SeverityLevel.HIGH.value
        elif score >= 0.3:
            severity_info['severity'] = SeverityLevel.MEDIUM.value
        else:
            severity_info['severity'] = SeverityLevel.LOW.value
        
        severity_info['score'] = score
        severity_info['confidence'] = min(score + 0.2, 1.0)
        severity_info['factors'] = factors
        
        return severity_info
    
    def analyze_bug_report(self, text: str, source_info: Dict = None) -> Dict[str, Any]:
        """
        Analyze a single bug report
        
        Args:
            text (str): Bug report text
            source_info (Dict): Additional source information
            
        Returns:
            Dict[str, Any]: Complete bug analysis
        """
        try:
            # Extract different aspects
            platform_info = self.extract_platform_info(text)
            error_info = self.extract_error_patterns(text)
            steps_info = self.extract_reproduction_steps(text)
            severity_info = self.assess_severity(text, platform_info, error_info, steps_info)
            
            # Combine all information
            analysis = {
                'platform_info': platform_info,
                'error_info': error_info,
                'reproduction_steps': steps_info,
                'severity_assessment': severity_info,
                'technical_details': self._generate_technical_details(platform_info, error_info, steps_info),
                'reproducibility_score': steps_info['confidence'],
                'overall_confidence': (platform_info['confidence'] + error_info['confidence'] + 
                                    steps_info['confidence'] + severity_info['confidence']) / 4
            }
            
            # Add source information if provided
            if source_info:
                analysis['source_info'] = source_info
            
            self.logger.info(f"Bug analysis completed with severity: {severity_info['severity']}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing bug report: {str(e)}")
            return {
                'platform_info': {'platform': 'Unknown', 'confidence': 0.0},
                'error_info': {'error_types': [], 'confidence': 0.0},
                'reproduction_steps': {'steps': [], 'confidence': 0.0},
                'severity_assessment': {'severity': SeverityLevel.MEDIUM.value, 'confidence': 0.1},
                'technical_details': 'Analysis failed due to error',
                'reproducibility_score': 0.0,
                'overall_confidence': 0.1,
                'error': str(e)
            }
    
    def _generate_technical_details(self, platform_info: Dict, error_info: Dict, steps_info: Dict) -> str:
        """
        Generate technical details summary
        
        Args:
            platform_info (Dict): Platform information
            error_info (Dict): Error information
            steps_info (Dict): Reproduction steps
            
        Returns:
            str: Technical details summary
        """
        details = []
        
        # Platform details
        if platform_info['platform'] != 'Unknown':
            details.append(f"Platform: {platform_info['platform']}")
        
        if platform_info['devices']:
            details.append(f"Devices: {', '.join(platform_info['devices'])}")
        
        if platform_info['os_versions']:
            details.append(f"OS Versions: {', '.join(platform_info['os_versions'])}")
        
        if platform_info['app_versions']:
            details.append(f"App Versions: {', '.join(platform_info['app_versions'])}")
        
        # Error details
        if error_info['error_types']:
            details.append(f"Error Types: {', '.join(error_info['error_types'])}")
        
        if error_info['error_messages']:
            details.append(f"Error Messages: {', '.join(error_info['error_messages'][:3])}")  # Limit to first 3
        
        # Reproduction steps
        if steps_info['steps']:
            details.append(f"Reproduction Steps: {'; '.join(steps_info['steps'][:3])}")  # Limit to first 3
        
        return '; '.join(details) if details else "No technical details extracted"
    
    def analyze_batch(self, bug_reports: pd.DataFrame, text_column: str = 'content') -> pd.DataFrame:
        """
        Analyze a batch of bug reports
        
        Args:
            bug_reports (pd.DataFrame): Bug reports data
            text_column (str): Column name containing text
            
        Returns:
            pd.DataFrame: Data with bug analysis results
        """
        try:
            results = []
            
            for idx, row in bug_reports.iterrows():
                text = row[text_column]
                source_info = {
                    'source_id': row.get('id', ''),
                    'source_type': row.get('source_type', ''),
                    'timestamp': row.get('timestamp', '')
                }
                
                analysis = self.analyze_bug_report(text, source_info)
                
                # Add analysis results to row
                result_row = row.copy()
                result_row['bug_analysis'] = json.dumps(analysis)
                result_row['severity'] = analysis['severity_assessment']['severity']
                result_row['severity_confidence'] = analysis['severity_assessment']['confidence']
                result_row['platform'] = analysis['platform_info']['platform']
                result_row['reproducibility_score'] = analysis['reproducibility_score']
                result_row['technical_details'] = analysis['technical_details']
                
                results.append(result_row)
            
            analyzed_df = pd.DataFrame(results)
            
            self.logger.info(f"Analyzed {len(analyzed_df)} bug reports")
            self.logger.info(f"Severity distribution: {analyzed_df['severity'].value_counts().to_dict()}")
            
            return analyzed_df
            
        except Exception as e:
            self.logger.error(f"Error in batch bug analysis: {str(e)}")
            raise
    
    def get_bug_analysis_stats(self, analyzed_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get bug analysis statistics
        
        Args:
            analyzed_data (pd.DataFrame): Analyzed bug data
            
        Returns:
            Dict[str, Any]: Bug analysis statistics
        """
        try:
            stats = {
                'total_analyzed': len(analyzed_data),
                'severity_distribution': analyzed_data['severity'].value_counts().to_dict(),
                'platform_distribution': analyzed_data['platform'].value_counts().to_dict(),
                'reproducibility_stats': {
                    'mean': analyzed_data['reproducibility_score'].mean(),
                    'median': analyzed_data['reproducibility_score'].median(),
                    'min': analyzed_data['reproducibility_score'].min(),
                    'max': analyzed_data['reproducibility_score'].max()
                },
                'severity_confidence_stats': {
                    'mean': analyzed_data['severity_confidence'].mean(),
                    'median': analyzed_data['severity_confidence'].median(),
                    'min': analyzed_data['severity_confidence'].min(),
                    'max': analyzed_data['severity_confidence'].max()
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting bug analysis stats: {str(e)}")
            raise
