# CrewAI Installation Guide

## Prerequisites

### System Requirements
- **Python**: 3.10 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 1GB free space
- **Network**: Internet connection for OpenAI API

### Required Accounts
- **OpenAI API Key**: Valid API key with credits
- **Git**: For version control (optional)

## Installation Steps

### 1. Clone or Download Project

```bash
# Clone the repository
git clone <repository-url>
cd crewai_intelligent_feedback_analysis_action

# Or download and extract the project files
```

### 2. Create Virtual Environment

```bash
# Create Python 3.10 virtual environment
python -m venv .venv310

# Activate virtual environment
# Windows:
.venv310\Scripts\Activate.ps1

# macOS/Linux:
source .venv310/bin/activate
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

#### Individual Package Installation (if needed)

If the requirements.txt installation fails, install packages individually:

```bash
# Install CrewAI ecosystem
pip install crewai>=0.1.0
pip install crewai-tools>=0.1.0

# Install OpenAI integration
pip install openai>=1.40.0

# Install data processing libraries
pip install pandas==2.1.4
pip install numpy==1.24.3
pip install scikit-learn==1.3.2

# Install NLP libraries
pip install nltk==3.8.1
pip install textblob==0.17.1

# Install utilities
pip install python-dotenv==1.0.0
pip install openpyxl==3.1.5
pip install requests==2.31.0

# Install visualization
pip install streamlit==1.29.0
pip install matplotlib==3.8.2
pip install seaborn==0.13.0
pip install plotly==5.17.0

# Install async support
pip install aiohttp>=3.8.0
```

## Configuration

### 1. Environment Variables

Create `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```bash
# OpenAI API Key (required for CrewAI agents)
OPENAI_API_KEY=your_openai_api_key_here

# OpenAI Model Configuration
OPENAI_MODEL_NAME=gpt-3.5-turbo

# CrewAI Configuration
CREWAI_LOG_LEVEL=INFO
CREWAI_MAX_ITERATIONS=5
CREWAI_AGENT_TIMEOUT=120

# Classification Thresholds
CLASSIFICATION_CONFIDENCE_THRESHOLD=0.7
BUG_SEVERITY_THRESHOLD=0.8
FEATURE_PRIORITY_THRESHOLD=0.6

# File Paths
DATA_DIR=data
OUTPUT_DIR=data
LOG_DIR=logs

# Agent Configuration
DEFAULT_AGENT_TEMPERATURE=0.1
MAX_AGENT_ITERATIONS=5
```

### 2. Verify OpenAI API Key

Test your OpenAI API key:

```python
import openai

# Test API connection
client = openai.OpenAI(api_key="your-api-key")
models = client.models.list()
print(f"API Key valid. Available models: {len(models.data)}")
```

## Data Setup

### 1. Verify Data Files

Ensure the following files exist in the `data/` directory:

```bash
data/
├── app_store_reviews.csv
├── support_emails.csv
└── expected_classifications.csv (optional)
```

### 2. Sample Data Format

**app_store_reviews.csv**:
```csv
review_id,platform,rating,review_text,user_name,date,app_version
REV001,Google Play,1,"App crashes when I try to sync",john_doe89,2024-03-15,3.2.1
```

**support_emails.csv**:
```csv
email_id,subject,body,sender_email,timestamp,priority
EMAIL001,App Crash Report,"Hi Support Team...",user@email.com,2024-03-15,high
```

## Testing Installation

### 1. Test Import

```bash
python -c "
from src.orchestration.crew_manager import FeedbackAnalysisCrew
print('✅ CrewAI system imported successfully')
"
```

### 2. Run Demo

```bash
python run_demo.py
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```
ModuleNotFoundError: No module named 'crewai'
```
**Solution**: Ensure virtual environment is activated and packages are installed.

#### 2. OpenAI API Errors
```
openai.AuthenticationError: Invalid API key
```
**Solution**: Verify API key in `.env` file.

#### 3. CrewAI Configuration Errors
```
ValueError: CrewAI initialization failed
```
**Solution**: Check environment variables and agent configuration.

#### 4. Streamlit Issues
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution**: Install streamlit: `pip install streamlit==1.29.0`

#### 5. Data File Errors
```
FileNotFoundError: data/app_store_reviews.csv
```
**Solution**: Ensure data files are in the correct directory.

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

#### 1. Slow Processing
- Reduce data size for testing
- Check OpenAI API rate limits
- Optimize agent task descriptions

#### 2. Memory Issues
- Process data in smaller batches
- Close unused applications
- Increase system RAM if possible

## Verification

### Complete System Check

Run this verification script:

```python
#!/usr/bin/env python3
import sys
import os

def check_system():
    print("🔍 CrewAI System Verification")
    print("=" * 40)
    
    # Check imports
    try:
        from src.orchestration.crew_manager import FeedbackAnalysisCrew
        print("✅ CrewAI system import: OK")
    except ImportError as e:
        print(f"❌ CrewAI system import: FAILED - {e}")
        return False
    
    # Check environment
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OpenAI API key: FOUND")
    else:
        print("❌ OpenAI API key: NOT FOUND")
        return False
    
    # Check data files
    data_files = ['data/app_store_reviews.csv', 'data/support_emails.csv']
    for file in data_files:
        if os.path.exists(file):
            print(f"✅ {file}: FOUND")
        else:
            print(f"❌ {file}: NOT FOUND")
            return False
    
    print("✅ All checks passed!")
    return True

if __name__ == "__main__":
    check_system()
```

## Next Steps

After successful installation:

1. **Run the demo**: `python run_demo.py`
2. **Start the dashboard**: `streamlit run src/ui/dashboard.py`
3. **Review documentation**: Check `docs/` directory for detailed guides
4. **Customize configuration**: Adjust thresholds and parameters
5. **Process your data**: Add your own CSV files to the data directory

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the CrewAI documentation
3. Verify OpenAI API status and credits
4. Check system requirements and compatibility
