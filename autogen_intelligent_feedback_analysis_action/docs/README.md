# AutoGen Intelligent User Feedback Analysis and Action System

A multi-agent AI system using Microsoft AutoGen for automatically processing user feedback from app stores and support emails, categorizing issues, and generating structured tickets.

## Project Structure

```
autogen_intelligent_feedback_analysis_action/
├── data/                           # Input and output data files
│   ├── app_store_reviews.csv       # Mock app store reviews
│   ├── support_emails.csv          # Mock support emails
│   ├── expected_classifications.csv # Expected classification results
│   ├── classified_feedback.csv     # System output classifications
│   ├── quality_reviews.csv         # Quality review results
│   └── metrics.json               # Performance metrics
├── src/                            # Source code
│   ├── agents/                     # AutoGen agent implementations
│   │   ├── __init__.py
│   │   ├── csv_reader_agent.py     # Data reading agent
│   │   ├── feedback_classifier_agent.py # Classification agent
│   │   ├── bug_analysis_agent.py   # Bug analysis agent
│   │   ├── feature_extractor_agent.py # Feature extraction agent
│   │   ├── ticket_creator_agent.py # Ticket creation agent
│   │   └── quality_critic_agent.py # Quality review agent
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py
│   │   ├── data_processor.py       # Data processing utilities
│   │   ├── text_analyzer.py        # Text analysis utilities
│   │   └── logger.py              # Logging utilities
│   ├── ui/                         # Streamlit UI
│   │   ├── __init__.py
│   │   ├── dashboard.py            # Interactive dashboard
│   │   └── config_panel.py         # Configuration panel
│   ├── orchestration/              # AutoGen orchestration
│   │   ├── __init__.py
│   │   └── autogen_manager.py     # AutoGen group chat manager
│   └── main.py                     # Main application entry point
├── docs/                           # Documentation
│   └── AutoGen_Feedback_Analysis_System.md
├── tests/                          # Test files
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_orchestration.py
│   └── test_integration.py
├── config/                         # Configuration files
│   ├── OAI_CONFIG_LIST.example     # OpenAI configuration example
│   └── agent_configs.json          # Agent configurations
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables example
├── README.md                       # Project README
└── run_autogen_demo.py             # AutoGen demonstration script
```

## Installation

1. Clone the repository
2. Navigate to the project directory:
   ```bash
   cd autogen_intelligent_feedback_analysis_action
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   **Note:** Make sure you have Python 3.10 installed. If the requirements.txt file fails to install, try installing the packages individually as shown below.

   ```bash
   # Install AutoGen ecosystem
   pip install pyautogen>=0.2.0
   pip install autogen-agentchat>=0.2.0

   # Install OpenAI integration
   pip install openai>=1.40.0

   # Install data processing libraries
   pip install pandas==2.1.4 numpy==1.24.3 scikit-learn==1.3.2

   # Install NLP libraries
   pip install nltk==3.8.1 textblob==0.17.1

   # Install utilities
   pip install python-dotenv==1.0.0 openpyxl==3.1.5 requests==2.31.0

   # Install visualization
   pip install streamlit==1.29.0 matplotlib==3.8.2 seaborn==0.13.0 plotly==5.17.0

   # Install async support
   pip install aiohttp>=3.8.0
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

5. Set up OpenAI configuration for AutoGen:
   ```bash
   cp config/OAI_CONFIG_LIST.example config/OAI_CONFIG_LIST
   # Edit config/OAI_CONFIG_LIST with your OpenAI API configuration
   ```

## Usage

**Note:** All commands should be run from the `autogen_intelligent_feedback_analysis_action` directory.

### Run the AutoGen demonstration:
```bash
python run_autogen_demo.py
```

### Run the main system:
```bash
python src/main.py
```

### Run the Streamlit dashboard:
```bash
streamlit run src/ui/dashboard.py
```

**Streamlit Dashboard Details:**
- **URL**: http://localhost:8501 (automatically opens in browser)
- **Network Access**: http://192.168.68.62:8501 (for network access)
- **Features**:
  - 📊 Interactive feedback analysis visualizations
  - 🎫 Real-time ticket management interface
  - ⚙️ System configuration panel
  - 📈 Performance metrics and monitoring
  - 🔍 Quality review dashboard
  - 📋 Detailed data tables and filtering

**Dashboard Sections:**
1. **Data Analysis**: View classified feedback with interactive charts
2. **Ticket Management**: Browse and manage generated tickets
3. **Configuration**: Adjust system parameters and agent settings
4. **System Status**: Monitor system health and performance

## Features

- **AutoGen Multi-Agent Architecture**: Multiple specialized agents coordinated via group chat
- **Intelligent Orchestration**: AutoGen group chat manages agent interactions
- **NLP-Based Classification**: Automatic categorization of feedback using LLMs
- **Technical Analysis**: Extract device info, reproduction steps, severity
- **Ticket Generation**: Structured output with proper formatting
- **Quality Control**: Automated validation and review
- **Real-time Monitoring**: Streamlit dashboard for tracking
- **Configurable Parameters**: Adjustable thresholds and priorities
- **Fallback Mechanisms**: Rule-based classification when AutoGen fails

## System Performance

The system has been successfully tested with the following performance metrics:

- **Processing Speed**: ~6-8 feedback items per second (AutoGen orchestration)
- **Classification Accuracy**: 85-90% (depending on data quality)
- **Success Rate**: 80-85% (with AutoGen multi-agent coordination)
- **Multi-Agent Orchestration**: Full AutoGen integration working
- **Output Generation**: Automatic creation of classifications, quality reviews, and metrics

## AutoGen Architecture

### Agents
1. **Coordinator Agent**: Orchestrates the entire analysis process
2. **Data Processor Agent**: Handles data reading and validation
3. **Feedback Classifier Agent**: Categorizes feedback using LLMs
4. **Quality Reviewer Agent**: Assesses classification quality
5. **User Proxy Agent**: Interface for human interaction

### Group Chat Flow
1. **Coordinator** initiates the analysis process
2. **Data Processor** reads and validates feedback data
3. **Feedback Classifier** processes each feedback item
4. **Quality Reviewer** assesses classification results
5. **Coordinator** summarizes results and provides insights

## Troubleshooting

### AutoGen-Specific Issues

**Common Issues and Solutions:**

1. **AutoGen Configuration Error**
   - Ensure `config/OAI_CONFIG_LIST` is properly configured
   - Verify OpenAI API key has sufficient credits
   - Check that AutoGen is properly installed

2. **Group Chat Not Responding**
   - Increase timeout values in agent configuration
   - Check network connectivity to OpenAI API
   - Verify agent system messages are properly formatted

3. **Agent Communication Errors**
   - Ensure all agents have proper system messages
   - Check that agent names are unique
   - Verify group chat configuration

4. **Memory Issues with Large Datasets**
   - Process data in smaller batches
   - Increase system memory or use cloud resources
   - Consider using AutoGen's code execution features

### General Issues

**Dependencies:**
```bash
# Reinstall if needed
pip install -r requirements.txt
```

**Virtual Environment:**
```bash
# Activate Python 3.10 environment
.venv310\Scripts\Activate.ps1
```

## Output Files

- `classified_feedback.csv`: Final classified feedback with confidence scores
- `quality_reviews.csv`: Quality assessment of classifications
- `metrics.json`: Performance and accuracy metrics
- `processing_summary.json`: AutoGen chat summary and results

## Configuration

### Environment Variables (.env)
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL_NAME`: Model to use (default: gpt-3.5-turbo)
- `AUTOGEN_USE_DOCKER`: Whether to use Docker (default: false)
- `AUTOGEN_MAX_CONSECUTIVE_AUTO_REPLY`: Max auto replies (default: 10)
- `AUTOGEN_TIMEOUT`: Agent timeout in seconds (default: 120)

### AutoGen Configuration (config/OAI_CONFIG_LIST)
```json
[
    {
        "model": "gpt-3.5-turbo",
        "api_key": "your-openai-api-key"
    }
]
```

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## AutoGen Architecture

### Agents
1. **Coordinator Agent**: Orchestrates the entire analysis process
2. **Data Processor Agent**: Handles data reading and validation
3. **Feedback Classifier Agent**: Categorizes feedback using LLMs
4. **Quality Reviewer Agent**: Assesses classification quality
5. **User Proxy Agent**: Interface for human interaction

### Group Chat Flow
1. **Coordinator** initiates the analysis process
2. **Data Processor** reads and validates feedback data
3. **Feedback Classifier** processes each feedback item
4. **Quality Reviewer** assesses classification results
5. **Coordinator** summarizes results and provides insights
