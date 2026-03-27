"""
AutoGen-based CSV Reader Agent for reading and parsing feedback data
"""

import pandas as pd
import logging
import os
from typing import Dict, List, Optional, Tuple
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class CSVReaderAgent:
    """
    AutoGen agent for reading and parsing feedback data from CSV files
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the CSV Reader Agent
        
        Args:
            data_dir (str): Directory containing CSV files
        """
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        
    def read_app_store_reviews(self) -> pd.DataFrame:
        """
        Read app store reviews from CSV file
        
        Returns:
            pd.DataFrame: App store reviews data
        """
        try:
            file_path = os.path.join(self.data_dir, 'app_store_reviews.csv')
            reviews_df = pd.read_csv(file_path)
            
            # Add missing priority column to reviews (default to 'medium')
            if 'priority' not in reviews_df.columns:
                reviews_df['priority'] = 'medium'
            
            self.logger.info(f"Read {len(reviews_df)} app store reviews")
            return reviews_df
        except Exception as e:
            self.logger.error(f"Error reading app store reviews: {str(e)}")
            raise
    
    def read_support_emails(self) -> pd.DataFrame:
        """
        Read support emails from CSV file
        
        Returns:
            pd.DataFrame: Support emails data
        """
        try:
            file_path = os.path.join(self.data_dir, 'support_emails.csv')
            emails_df = pd.read_csv(file_path)
            
            # Validate required columns
            required_columns = ['email_id', 'subject', 'body', 'sender_email', 'timestamp', 'priority']
            missing_columns = [col for col in required_columns if col not in emails_df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns in support emails: {missing_columns}")
            
            self.logger.info(f"Read {len(emails_df)} support emails")
            return emails_df
        except Exception as e:
            self.logger.error(f"Error reading support emails: {str(e)}")
            raise
    
    def combine_feedback_data(self) -> pd.DataFrame:
        """
        Combine reviews and emails into a single dataset
        
        Returns:
            pd.DataFrame: Combined feedback data
        """
        try:
            # Read both data sources
            reviews_df = self.read_app_store_reviews()
            emails_df = self.read_support_emails()
            
            # Standardize column names
            reviews_df['content'] = reviews_df['review_text']
            reviews_df['id'] = reviews_df['review_id']
            reviews_df['timestamp'] = reviews_df['date']
            
            emails_df['content'] = emails_df['body']
            emails_df['id'] = emails_df['email_id']
            
            # Select common columns
            common_columns = ['id', 'content', 'timestamp', 'priority']
            
            reviews_subset = reviews_df[common_columns + ['platform', 'rating', 'user_name', 'app_version']]
            reviews_subset['source_type'] = 'app_store_review'
            
            emails_subset = emails_df[common_columns + ['subject', 'sender_email']]
            emails_subset['source_type'] = 'support_email'
            
            # Combine datasets
            combined_df = pd.concat([reviews_subset, emails_subset], ignore_index=True)
            
            self.logger.info(f"Combined {len(reviews_df)} reviews and {len(emails_df)} emails into {len(combined_df)} total feedback items")
            return combined_df
        except Exception as e:
            self.logger.error(f"Error combining feedback data: {str(e)}")
            raise
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate the combined feedback data
        
        Args:
            df (pd.DataFrame): Combined feedback data
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        try:
            required_columns = ['id', 'content', 'source_type', 'timestamp']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return False
            
            if df.empty:
                self.logger.error("DataFrame is empty")
                return False
            
            # Check for null values in critical columns
            null_counts = df[required_columns].isnull().sum()
            if null_counts.any():
                self.logger.warning(f"Null values found in critical columns: {null_counts[null_counts > 0].to_dict()}")
            
            self.logger.info("Data validation passed")
            return True
        except Exception as e:
            self.logger.error(f"Error validating data: {str(e)}")
            return False
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """
        Get summary statistics of the feedback data
        
        Args:
            df (pd.DataFrame): Feedback data
            
        Returns:
            Dict: Summary statistics
        """
        try:
            summary = {
                'total_items': len(df),
                'source_breakdown': df['source_type'].value_counts().to_dict(),
                'date_range': {
                    'start': df['timestamp'].min(),
                    'end': df['timestamp'].max()
                },
                'avg_content_length': df['content'].str.len().mean(),
                'null_counts': df.isnull().sum().to_dict()
            }
            
            self.logger.info("Generated data summary")
            return summary
        except Exception as e:
            self.logger.error(f"Error generating data summary: {str(e)}")
            return {}
