"""
Feedback Classifier Agent - Categorizes feedback using NLP (bug, feature request, praise, complaint, spam)
"""

import pandas as pd
import logging
import re
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import json
from crewai import Agent
from langchain_openai import ChatOpenAI

class FeedbackClassifierAgent:
    """
    Agent responsible for categorizing user feedback into:
    - Bug
    - Feature Request
    - Praise
    - Complaint
    - Spam
    """
    
    def __init__(self, model_dir: str = "models", confidence_threshold: float = 0.7):
        """
        Initialize the Feedback Classifier Agent
        
        Args:
            model_dir (str): Directory to save/load trained models
            confidence_threshold (float): Minimum confidence for classification
        """
        self.model_dir = model_dir
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
        
        # Categories
        self.categories = ['Bug', 'Feature Request', 'Praise', 'Complaint', 'Spam']
        
        # Initialize ML pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                lowercase=True
            )),
            ('classifier', MultinomialNB())
        ])
        
        # Keywords for rule-based classification
        self.keyword_patterns = {
            'Bug': [
                r'crash', r'error', r'bug', r'broken', r'not working', r'freeze',
                r'login issue', r'can\'t login', r'crashes', r'glitch', r'malfunction',
                r'data loss', r'sync issue', r'fail', r'problem', r'issue'
            ],
            'Feature Request': [
                r'please add', r'would love to see', r'feature request', r'suggestion',
                r'add functionality', r'missing', r'would be nice', r'implement',
                r'new feature', r'enhancement', r'improvement', r'wish'
            ],
            'Praise': [
                r'amazing', r'love', r'great', r'excellent', r'perfect', r'awesome',
                r'fantastic', r'wonderful', r'best', r'brilliant', r'thank you',
                r'works perfectly', r'beautiful', r'impressed'
            ],
            'Complaint': [
                r'too expensive', r'poor', r'slow', r'bad', r'terrible', r'frustrating',
                r'disappointed', r'annoying', r'useless', r'waste', r'money',
                r'customer service', r'cancel', r'subscription'
            ],
            'Spam': [
                r'asdf', r'random', r'promo', r'spam', r'advertisement', r'unrelated',
                r'123', r'test', r'nonsense', r'garbage', r'random characters'
            ]
        }
        
        # Create CrewAI agent
        self.agent = Agent(
            role="Feedback Classification Specialist",
            goal="Accurately categorize user feedback into Bug, Feature Request, Praise, Complaint, or Spam",
            backstory="You are an expert NLP specialist trained to analyze user feedback and classify it with high accuracy.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Model file path
        self.model_file = os.path.join(model_dir, "feedback_classifier_model.joblib")
        
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for classification
        
        Args:
            text (str): Input text
            
        Returns:
            str: Preprocessed text
        """
        if pd.isna(text) or text is None:
            return ""
        
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def rule_based_classification(self, text: str) -> Tuple[str, float]:
        """
        Rule-based classification using keyword patterns
        
        Args:
            text (str): Input text
            
        Returns:
            Tuple[str, float]: (category, confidence)
        """
        text_lower = text.lower()
        category_scores = {}
        
        for category, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            
            # Normalize score by text length
            if len(text) > 0:
                category_scores[category] = score / len(text.split())
            else:
                category_scores[category] = 0
        
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            confidence = min(category_scores[best_category] * 10, 1.0)  # Scale to 0-1
            return best_category, confidence
        else:
            return 'Bug', 0.1  # Default category
    
    def sentiment_analysis(self, text: str) -> Dict[str, float]:
        """
        Perform sentiment analysis using TextBlob
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, float]: Sentiment scores
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1 (negative to positive)
            subjectivity = blob.sentiment.subjectivity  # 0 to 1 (objective to subjective)
            
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'sentiment_label': 'positive' if polarity > 0.1 else 'negative' if polarity < -0.1 else 'neutral'
            }
        except:
            return {
                'polarity': 0.0,
                'subjectivity': 0.0,
                'sentiment_label': 'neutral'
            }
    
    def extract_features(self, text: str) -> Dict[str, Any]:
        """
        Extract features from text for classification
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, Any]: Extracted features
        """
        features = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'has_numbers': bool(re.search(r'\d', text)),
            'has_exclamation': bool(re.search(r'!', text)),
            'has_question': bool(re.search(r'\?', text)),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            'sentiment': self.sentiment_analysis(text)
        }
        
        return features
    
    def classify_single_feedback(self, text: str, use_ml: bool = True) -> Dict[str, Any]:
        """
        Classify a single feedback text
        
        Args:
            text (str): Feedback text
            use_ml (bool): Whether to use ML model (fallback to rule-based)
            
        Returns:
            Dict[str, Any]: Classification result with confidence
        """
        try:
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            # Extract features
            features = self.extract_features(text)
            
            # Rule-based classification
            rule_category, rule_confidence = self.rule_based_classification(processed_text)
            
            # ML classification (if model is trained and use_ml is True)
            ml_category, ml_confidence = rule_category, rule_confidence
            
            if use_ml and os.path.exists(self.model_file):
                try:
                    # Load and use trained model
                    model = joblib.load(self.model_file)
                    
                    # Predict with ML model
                    ml_proba = model.predict_proba([processed_text])[0]
                    ml_pred_idx = np.argmax(ml_proba)
                    ml_category = self.categories[ml_pred_idx]
                    ml_confidence = ml_proba[ml_pred_idx]
                    
                except Exception as e:
                    self.logger.warning(f"ML model prediction failed: {str(e)}. Using rule-based.")
            
            # Combine results (prefer ML if confidence is high enough)
            if ml_confidence >= self.confidence_threshold:
                final_category = ml_category
                final_confidence = ml_confidence
                method = "ML"
            else:
                final_category = rule_category
                final_confidence = rule_confidence
                method = "Rule-based"
            
            # Adjust based on sentiment for certain categories
            sentiment = features['sentiment']
            if sentiment['sentiment_label'] == 'positive' and final_category == 'Complaint':
                # If sentiment is positive but classified as complaint, reconsider
                if rule_category in ['Praise', 'Feature Request']:
                    final_category = rule_category
                    method = "Sentiment-adjusted"
            elif sentiment['sentiment_label'] == 'negative' and final_category == 'Praise':
                # If sentiment is negative but classified as praise, reconsider
                if rule_category in ['Bug', 'Complaint']:
                    final_category = rule_category
                    method = "Sentiment-adjusted"
            
            return {
                'category': final_category,
                'confidence': final_confidence,
                'method': method,
                'features': features,
                'rule_based': (rule_category, rule_confidence),
                'ml_based': (ml_category, ml_confidence)
            }
            
        except Exception as e:
            self.logger.error(f"Error classifying feedback: {str(e)}")
            return {
                'category': 'Bug',
                'confidence': 0.1,
                'method': 'Error-fallback',
                'features': {},
                'rule_based': ('Bug', 0.1),
                'ml_based': ('Bug', 0.1)
            }
    
    def classify_batch(self, feedback_data: pd.DataFrame, text_column: str = 'content') -> pd.DataFrame:
        """
        Classify a batch of feedback
        
        Args:
            feedback_data (pd.DataFrame): Feedback data
            text_column (str): Column name containing text
            
        Returns:
            pd.DataFrame: Data with classification results
        """
        try:
            results = []
            
            for idx, row in feedback_data.iterrows():
                text = row[text_column]
                classification = self.classify_single_feedback(text)
                
                # Add classification results to row
                result_row = row.copy()
                result_row['predicted_category'] = classification['category']
                result_row['classification_confidence'] = classification['confidence']
                result_row['classification_method'] = classification['method']
                
                results.append(result_row)
            
            classified_df = pd.DataFrame(results)
            
            self.logger.info(f"Classified {len(classified_df)} feedback items")
            self.logger.info(f"Category distribution: {classified_df['predicted_category'].value_counts().to_dict()}")
            
            return classified_df
            
        except Exception as e:
            self.logger.error(f"Error in batch classification: {str(e)}")
            raise
    
    def train_model(self, training_data: pd.DataFrame, text_column: str = 'content', 
                   label_column: str = 'category') -> Dict[str, Any]:
        """
        Train the ML classification model
        
        Args:
            training_data (pd.DataFrame): Training data
            text_column (str): Column name containing text
            label_column (str): Column name containing labels
            
        Returns:
            Dict[str, Any]: Training results
        """
        try:
            # Prepare data
            X = training_data[text_column].apply(self.preprocess_text)
            y = training_data[label_column]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            self.pipeline.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.pipeline.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, output_dict=True)
            
            # Save model
            joblib.dump(self.pipeline, self.model_file)
            
            self.logger.info(f"Model trained with accuracy: {accuracy:.3f}")
            
            return {
                'accuracy': accuracy,
                'classification_report': report,
                'model_file': self.model_file,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}")
            raise
    
    def evaluate_classification(self, classified_data: pd.DataFrame, 
                               expected_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate classification accuracy against expected results
        
        Args:
            classified_data (pd.DataFrame): Classified data
            expected_data (pd.DataFrame): Expected classifications
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        try:
            # Merge classified and expected data
            merged = pd.merge(
                classified_data, 
                expected_data, 
                left_on='id', 
                right_on='source_id',
                how='inner'
            )
            
            if len(merged) == 0:
                return {
                    'error': 'No matching records found between classified and expected data',
                    'total_classified': len(classified_data),
                    'total_expected': len(expected_data)
                }
            
            # Calculate accuracy
            correct_predictions = (merged['predicted_category'] == merged['category']).sum()
            total_predictions = len(merged)
            accuracy = correct_predictions / total_predictions
            
            # Category-wise accuracy
            category_accuracy = {}
            for category in self.categories:
                category_data = merged[merged['category'] == category]
                if len(category_data) > 0:
                    cat_correct = (category_data['predicted_category'] == category_data['category']).sum()
                    category_accuracy[category] = cat_correct / len(category_data)
                else:
                    category_accuracy[category] = 0.0
            
            # Confidence analysis
            avg_confidence = merged['classification_confidence'].mean()
            
            return {
                'overall_accuracy': accuracy,
                'category_accuracy': category_accuracy,
                'average_confidence': avg_confidence,
                'total_evaluated': total_predictions,
                'correct_predictions': correct_predictions,
                'misclassified': merged[merged['predicted_category'] != merged['category']].to_dict('records')
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating classification: {str(e)}")
            raise
    
    def get_classification_stats(self, classified_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get classification statistics
        
        Args:
            classified_data (pd.DataFrame): Classified data
            
        Returns:
            Dict[str, Any]: Classification statistics
        """
        try:
            stats = {
                'total_classified': len(classified_data),
                'category_distribution': classified_data['predicted_category'].value_counts().to_dict(),
                'confidence_stats': {
                    'mean': classified_data['classification_confidence'].mean(),
                    'median': classified_data['classification_confidence'].median(),
                    'min': classified_data['classification_confidence'].min(),
                    'max': classified_data['classification_confidence'].max()
                },
                'method_distribution': classified_data['classification_method'].value_counts().to_dict()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting classification stats: {str(e)}")
            raise
