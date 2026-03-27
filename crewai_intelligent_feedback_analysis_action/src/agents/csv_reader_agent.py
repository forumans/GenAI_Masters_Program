"""
CSV Reader Agent - Reads and parses feedback data from CSV files
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from crewai import Agent
from langchain_openai import ChatOpenAI

class CSVReaderAgent:
    """
    Agent responsible for reading and parsing feedback data from CSV files.
    Handles both app store reviews and support emails.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the CSV Reader Agent
        
        Args:
            data_dir (str): Directory containing CSV files
        """
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
        
        # File paths
        self.reviews_file = os.path.join(data_dir, "app_store_reviews.csv")
        self.emails_file = os.path.join(data_dir, "support_emails.csv")
        self.expected_file = os.path.join(data_dir, "expected_classifications.csv")
        
        # Create CrewAI agent
        self.agent = Agent(
            role="CSV Data Reader",
            goal="Read and parse feedback data from CSV files accurately",
            backstory="You are an expert data processor specializing in reading and validating CSV files containing user feedback data.",
            verbose=True,
            allow_delegation=False,
            llm="gpt-3.5-turbo"
        )
    
    def validate_file_exists(self, file_path: str) -> bool:
        """Check if file exists and is readable"""
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                return False
            
            # Try to read first few rows to validate
            df_sample = pd.read_csv(file_path, nrows=1)
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating file {file_path}: {str(e)}")
            return False
    
    def read_app_store_reviews(self) -> pd.DataFrame:
        """
        Read app store reviews from CSV file
        
        Returns:
            pd.DataFrame: App store reviews data
        """
        try:
            if not self.validate_file_exists(self.reviews_file):
                raise FileNotFoundError(f"Reviews file not found: {self.reviews_file}")
            
            df = pd.read_csv(self.reviews_file)
            
            # Validate required columns
            required_columns = ['review_id', 'platform', 'rating', 'review_text', 'user_name', 'date', 'app_version']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns in reviews file: {missing_columns}")
            
            # Clean and validate data
            df = self._clean_reviews_data(df)
            
            self.logger.info(f"Successfully read {len(df)} app store reviews")
            return df
            
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
            if not self.validate_file_exists(self.emails_file):
                raise FileNotFoundError(f"Emails file not found: {self.emails_file}")
            
            df = pd.read_csv(self.emails_file)
            
            # Validate required columns
            required_columns = ['email_id', 'subject', 'body', 'sender_email', 'timestamp', 'priority']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns in emails file: {missing_columns}")
            
            # Clean and validate data
            df = self._clean_emails_data(df)
            
            self.logger.info(f"Successfully read {len(df)} support emails")
            return df
            
        except Exception as e:
            self.logger.error(f"Error reading support emails: {str(e)}")
            raise
    
    def read_expected_classifications(self) -> pd.DataFrame:
        """
        Read expected classifications for validation
        
        Returns:
            pd.DataFrame: Expected classifications data
        """
        try:
            if not self.validate_file_exists(self.expected_file):
                raise FileNotFoundError(f"Expected classifications file not found: {self.expected_file}")
            
            df = pd.read_csv(self.expected_file)
            
            # Validate required columns
            required_columns = ['source_id', 'source_type', 'category', 'priority', 'technical_details', 'suggested_title']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns in expected classifications file: {missing_columns}")
            
            self.logger.info(f"Successfully read {len(df)} expected classifications")
            return df
            
        except Exception as e:
            self.logger.error(f"Error reading expected classifications: {str(e)}")
            raise
    
    def _clean_reviews_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate reviews data"""
        # Remove duplicates
        df = df.drop_duplicates(subset=['review_id'])
        
        # Fill missing values
        df['review_text'] = df['review_text'].fillna('')
        df['user_name'] = df['user_name'].fillna('Anonymous')
        df['app_version'] = df['app_version'].fillna('Unknown')
        
        # Validate rating
        df = df[df['rating'].between(1, 5)]
        
        # Add source type
        df['source_type'] = 'review'
        
        return df
    
    def _clean_emails_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate emails data"""
        # Remove duplicates
        df = df.drop_duplicates(subset=['email_id'])
        
        # Fill missing values
        df['subject'] = df['subject'].fillna('No Subject')
        df['body'] = df['body'].fillna('')
        df['priority'] = df['priority'].fillna('Medium')
        
        # Add source type
        df['source_type'] = 'email'
        
        return df
    
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
            
            # Add missing priority column to reviews (default to 'medium')
            if 'priority' not in reviews_df.columns:
                reviews_df['priority'] = 'medium'
            
            emails_df['content'] = emails_df['body']
            emails_df['id'] = emails_df['email_id']
            
            # Select common columns
            common_columns = ['id', 'source_type', 'content', 'timestamp', 'priority']
            
            reviews_subset = reviews_df[common_columns + ['platform', 'rating', 'user_name', 'app_version']]
            emails_subset = emails_df[common_columns + ['subject', 'sender_email']]
            
            # Combine datasets
            combined_df = pd.concat([reviews_subset, emails_subset], ignore_index=True)
            
            self.logger.info(f"Combined {len(reviews_df)} reviews and {len(emails_df)} emails into {len(combined_df)} total feedback items")
            
            return combined_df
            
        except Exception as e:
            self.logger.error(f"Error combining feedback data: {str(e)}")
            raise
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the data
        
        Returns:
            Dict[str, Any]: Data summary statistics
        """
        try:
            reviews_df = self.read_app_store_reviews()
            emails_df = self.read_support_emails()
            
            summary = {
                'total_reviews': len(reviews_df),
                'total_emails': len(emails_df),
                'total_feedback': len(reviews_df) + len(emails_df),
                'review_platforms': reviews_df['platform'].value_counts().to_dict(),
                'review_ratings': reviews_df['rating'].value_counts().to_dict(),
                'email_priorities': emails_df['priority'].value_counts().to_dict(),
                'date_range': {
                    'earliest': min(reviews_df['date'].min(), emails_df['timestamp'].min()),
                    'latest': max(reviews_df['date'].max(), emails_df['timestamp'].max())
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating data summary: {str(e)}")
            raise
    
    def process_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Process all CSV files and return combined data
        
        Returns:
            Dict[str, pd.DataFrame]: All processed data
        """
        try:
            data_dict = {
                'reviews': self.read_app_store_reviews(),
                'emails': self.read_support_emails(),
                'expected_classifications': self.read_expected_classifications(),
                'combined': self.combine_feedback_data()
            }
            
            self.logger.info("Successfully processed all CSV files")
            return data_dict
            
        except Exception as e:
            self.logger.error(f"Error processing all data: {str(e)}")
            raise
