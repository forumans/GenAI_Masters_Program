# Intelligent User Feedback Analysis and Action System

A multi-agent AI system that automatically processes user feedback from app stores and support emails, categorizes issues, and generates structured tickets.

## Project Structure

```
crewai_intelligent_feedback_analysis_action/
├── data/                           # Input and output data files
│   ├── app_store_reviews.csv       # Mock app store reviews
│   ├── support_emails.csv          # Mock support emails
│   ├── expected_classifications.csv # Expected classification results
│   ├── generated_tickets.csv       # System output tickets
│   ├── processing_log.csv          # Processing logs
│   └── metrics.csv                 # Performance metrics
├── src/                            # Source code
│   ├── agents/                     # Agent implementations
│   │   ├── __init__.py
│   │   ├── csv_reader_agent.py
│   │   ├── feedback_classifier_agent.py
│   │   ├── bug_analysis_agent.py
│   │   ├── feature_extractor_agent.py
│   │   ├── ticket_creator_agent.py
│   │   └── quality_critic_agent.py
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py
│   │   ├── data_processor.py
│   │   ├── text_analyzer.py
│   │   └── logger.py
│   ├── ui/                         # Streamlit UI
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   └── config_panel.py
│   ├── orchestration/              # Multi-agent orchestration
│   │   ├── __init__.py
│   │   └── crew_manager.py
│   └── main.py                     # Main application entry point
├── docs/                           # Documentation
│   └── Intelligent_User_Feedback_Analysis_System.md
├── tests/                          # Test files
│   ├── __init__.py
│   ├── test_agents.py
│   └── test_system.py
├── config/                         # Configuration files
│   ├── settings.py
│   └── prompts.py
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables example
├── README.md                       # Project README
└── run_demo.py                     # Demonstration script
```

## Installation

1. Clone the repository
2. Navigate to the project directory:
   ```bash
   cd crewai_intelligent_feedback_analysis_action
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   **Note:** Make sure you have Python 3.10 installed. If the requirements.txt file fails to install, try installing the packages individually as shown below.

   ```bash
   # Install data processing libraries first
   pip install pandas==2.1.4 numpy==1.24.3 scikit-learn==1.3.2

   # Install NLP libraries
   pip install nltk==3.8.1 textblob==0.17.1

   # Install utilities
   pip install python-dotenv==1.0.0 openpyxl==3.1.5 requests==2.31.0

   # Install visualization
   pip install streamlit==1.29.0 matplotlib==3.8.2 seaborn==0.13.0 plotly==5.17.0

   # Install AI/ML ecosystem
   pip install openai>=1.40.0 langchain>=0.2.0 langchain-openai>=0.1.0

   # Install CrewAI last
   pip install crewai>=0.86.0 crewai-tools>=0.25.0
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

## Usage

**Note:** All commands should be run from the `crewai_intelligent_feedback_analysis_action` directory.

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

### Run the demonstration:
```bash
python run_demo.py
```

## Features

- **Multi-Agent Architecture**: Six specialized agents for different tasks
- **NLP-Based Classification**: Automatic categorization of feedback
- **Technical Analysis**: Extract device info, reproduction steps, severity
- **Ticket Generation**: Structured output with proper formatting
- **Quality Control**: Automated validation and review
- **Real-time Monitoring**: Streamlit dashboard for tracking
- **Configurable Parameters**: Adjustable thresholds and priorities

## System Performance

The system has been successfully tested with the following performance metrics:

- **Processing Speed**: ~8.8 feedback items per second
- **Classification Accuracy**: 88.00%
- **Success Rate**: 84% (21/25 items successfully processed)
- **Multi-Agent Orchestration**: Full CrewAI integration working
- **Output Generation**: Automatic creation of tickets, quality reviews, and metrics

## Troubleshooting

### Streamlit Dashboard Issues

**Common Issues and Solutions:**

1. **ModuleNotFoundError: No module named 'src'**
   - Ensure you're running from the project directory: `crewai_intelligent_feedback_analysis_action`
   - Check that virtual environment is activated

2. **OpenAI API Key Error**
   - Verify `.env` file exists with `OPENAI_API_KEY` set
   - Ensure API key is valid and has credits

3. **Port Already in Use**
   - Streamlit automatically uses available ports
   - Access via the URL shown in terminal output

4. **Empty Data Visualizations**
   - Run `python run_demo.py` first to generate sample data
   - Check `data/` directory for generated files

5. **Dashboard Not Loading**
   - Stop server with `Ctrl+C` and restart
   - Check terminal for specific error messages

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

## Agents

1. **CSV Reader Agent**: Reads and parses feedback data from CSV files
2. **Feedback Classifier Agent**: Categorizes feedback using NLP
3. **Bug Analysis Agent**: Extracts technical details from bug reports
4. **Feature Extractor Agent**: Analyzes feature requests
5. **Ticket Creator Agent**: Generates structured tickets
6. **Quality Critic Agent**: Reviews and validates tickets

## Output Files

- `generated_tickets.csv`: Final structured tickets
- `processing_log.csv`: Detailed processing history
- `metrics.csv`: Performance and accuracy metrics
