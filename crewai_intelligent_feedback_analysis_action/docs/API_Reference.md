# CrewAI API Reference

## Core Classes

### FeedbackAnalysisCrew

Main orchestration class for the CrewAI feedback analysis system.

#### Constructor

```python
FeedbackAnalysisCrew(
    data_dir: str = "data",
    output_dir: str = "data",
    confidence_threshold: float = 0.7
)
```

**Parameters:**
- `data_dir` (str): Directory containing input data files
- `output_dir` (str): Directory for output files
- `confidence_threshold` (float): Minimum confidence for classification

**Example:**
```python
from src.orchestration.crew_manager import FeedbackAnalysisCrew

crew = FeedbackAnalysisCrew(
    data_dir="data",
    output_dir="output",
    confidence_threshold=0.8
)
```

#### Methods

##### process_feedback_data()

Process feedback data using CrewAI agents.

```python
process_feedback_data() -> Dict
```

**Returns:**
```python
{
    'status': 'success',
    'processing_time': 45.2,
    'total_processed': 25,
    'successful': 21,
    'failed': 4,
    'classification_accuracy': 0.88,
    'output_files': {
        'classified_feedback': 'path/to/file.csv',
        'generated_tickets': 'path/to/tickets.csv',
        # ... other files
    },
    'task_summary': 'All tasks completed successfully'
}
```

**Example:**
```python
results = crew.process_feedback_data()
print(f"Processed {results['total_processed']} items")
```

##### get_processing_status()

Get current processing status and configuration.

```python
get_processing_status() -> Dict
```

**Returns:**
```python
{
    'system_type': 'CrewAI',
    'agents_initialized': True,
    'tasks_defined': True,
    'data_directory': 'data',
    'output_directory': 'data',
    'confidence_threshold': 0.7,
    'timestamp': '2024-03-23T19:15:00'
}
```

---

## Agent Classes

### CSVReaderAgent

Handles reading and validation of feedback data from CSV files.

#### Constructor

```python
CSVReaderAgent(data_dir: str = "data")
```

#### Methods

##### read_app_store_reviews()

Read app store reviews from CSV.

```python
read_app_store_reviews() -> pd.DataFrame
```

##### read_support_emails()

Read support emails from CSV.

```python
read_support_emails() -> pd.DataFrame
```

##### combine_feedback_data()

Combine reviews and emails into single dataset.

```python
combine_feedback_data() -> pd.DataFrame
```

##### validate_data()

Validate feedback data structure.

```python
validate_data(df: pd.DataFrame) -> bool
```

---

### FeedbackClassifierAgent

Classifies feedback using CrewAI agents with rule-based fallback.

#### Constructor

```python
FeedbackClassifierAgent(
    model_dir: str = "models",
    confidence_threshold: float = 0.7
)
```

#### Methods

##### classify_feedback()

Classify a single feedback item.

```python
classify_feedback(feedback_text: str) -> Dict
```

**Returns:**
```python
{
    'category': 'Bug',
    'confidence': 0.85,
    'reasoning': 'User reports app crashing'
}
```

##### classify_batch()

Classify multiple feedback items.

```python
classify_batch(feedback_df: pd.DataFrame) -> pd.DataFrame
```

---

### BugAnalysisAgent

Analyzes bug reports for technical details and severity.

#### Constructor

```python
BugAnalysisAgent(severity_threshold: float = 0.8)
```

#### Methods

##### analyze_bug_report()

Analyze a single bug report.

```python
analyze_bug_report(feedback_text: str, feedback_id: str = "") -> Dict
```

**Returns:**
```python
{
    'severity': 'High',
    'category': 'crash',
    'device_info': 'Android 12 on Samsung Galaxy S21',
    'reproduction_steps': ['Step 1', 'Step 2'],
    'error_message': 'App crashes when syncing data',
    'confidence': 0.85,
    'reasoning': 'Critical crash with device details'
}
```

##### analyze_batch()

Analyze multiple bug reports.

```python
analyze_batch(bug_df: pd.DataFrame) -> pd.DataFrame
```

##### get_severity_distribution()

Get distribution of bug severities.

```python
get_severity_distribution(analyzed_df: pd.DataFrame) -> Dict
```

---

### FeatureExtractorAgent

Extracts and analyzes feature requests.

#### Constructor

```python
FeatureExtractorAgent(impact_threshold: float = 0.6)
```

#### Methods

##### extract_feature_info()

Extract information from feature request.

```python
extract_feature_info(feedback_text: str, feedback_id: str = "") -> Dict
```

**Returns:**
```python
{
    'category': 'UI/UX',
    'priority': 'High',
    'impact_score': 0.8,
    'complexity': 'Medium',
    'target_users': 'Power users',
    'benefits': ['Improved productivity', 'Better UX'],
    'confidence': 0.85,
    'reasoning': 'High impact feature for power users'
}
```

##### extract_batch()

Extract from multiple feature requests.

```python
extract_batch(feature_df: pd.DataFrame) -> pd.DataFrame
```

##### get_feature_statistics()

Get feature analysis statistics.

```python
get_feature_statistics(extracted_df: pd.DataFrame) -> Dict
```

---

### TicketCreatorAgent

Creates structured tickets from analyzed feedback.

#### Constructor

```python
TicketCreatorAgent(auto_approve: bool = False)
```

#### Methods

##### create_ticket()

Create a single ticket.

```python
create_ticket(feedback_data: Dict, analysis_data: Dict = None) -> Dict
```

**Returns:**
```python
{
    'ticket_id': 'TK-20240323-ABC123',
    'title': '[Bug] App crashes when syncing data',
    'description': 'Detailed description...',
    'type': 'Bug',
    'priority': 'High',
    'status': 'Open',
    'assignee': 'Senior Developer',
    'labels': ['bug', 'crash', 'sync'],
    'estimated_effort': '5',
    'reproduction_steps': 'Step 1, Step 2',
    'expected_outcome': '',
    'created_at': '2024-03-23T19:15:00',
    'confidence': 0.85
}
```

##### create_batch_tickets()

Create multiple tickets.

```python
create_batch_tickets(feedback_df: pd.DataFrame, analysis_df: pd.DataFrame = None) -> pd.DataFrame
```

##### save_tickets()

Save tickets to CSV file.

```python
save_tickets(tickets_df: pd.DataFrame, output_path: str) -> bool
```

---

### QualityCriticAgent

Reviews and validates ticket quality.

#### Constructor

```python
QualityCriticAgent(min_quality_score: float = 0.7)
```

#### Methods

##### review_ticket_quality()

Review quality of a single ticket.

```python
review_ticket_quality(ticket_data: Dict) -> Dict
```

**Returns:**
```python
{
    'ticket_id': 'TK-20240323-ABC123',
    'overall_score': 0.85,
    'quality_level': 'Good',
    'completeness_score': 0.9,
    'accuracy_score': 0.8,
    'clarity_score': 0.85,
    'relevance_score': 0.9,
    'actionability_score': 0.8,
    'issues': [],
    'suggestions': ['Add more specific error details'],
    'needs_manual_review': False,
    'reasoning': 'Good quality but could be more specific'
}
```

##### review_batch_tickets()

Review multiple tickets.

```python
review_batch_tickets(tickets_df: pd.DataFrame) -> pd.DataFrame
```

##### get_quality_metrics()

Get quality metrics from reviews.

```python
get_quality_metrics(reviews_df: pd.DataFrame) -> Dict
```

---

## Utility Functions

### Data Validation

```python
def validate_csv_structure(file_path: str, required_columns: List[str]) -> bool
```

### Configuration Loading

```python
def load_crewai_config(config_path: str) -> Dict
```

### Error Handling

```python
def handle_crewai_error(error: Exception, fallback_function: callable) -> Any
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL_NAME` | OpenAI model to use | `gpt-3.5-turbo` |
| `CREWAI_LOG_LEVEL` | Logging level | `INFO` |
| `CREWAI_MAX_ITERATIONS` | Max agent iterations | `5` |
| `CREWAI_AGENT_TIMEOUT` | Agent timeout (seconds) | `120` |
| `CLASSIFICATION_CONFIDENCE_THRESHOLD` | Min confidence for classification | `0.7` |
| `BUG_SEVERITY_THRESHOLD` | Bug severity threshold | `0.8` |
| `FEATURE_PRIORITY_THRESHOLD` | Feature priority threshold | `0.6` |

### CrewAI Configuration

CrewAI agents are configured through:

```python
from crewai import Agent, Task, Crew

# Define agents
agents = [
    Agent(
        role='Data Reader',
        goal='Read and validate feedback data',
        backstory='Expert in data processing',
        tools=[csv_reader_tool]
    ),
    # ... other agents
]

# Define tasks
tasks = [
    Task(
        description='Read feedback data from CSV files',
        agent=agents[0],
        expected_output='Validated feedback DataFrame'
    ),
    # ... other tasks
]

# Create crew
crew = Crew(
    agents=agents,
    tasks=tasks,
    verbose=True
)
```

---

## Error Handling

### Common Exceptions

#### CrewAIConfigurationError
Raised when CrewAI configuration is invalid.

#### DataValidationError
Raised when input data doesn't meet requirements.

#### AgentProcessingError
Raised when agent processing fails.

#### QualityReviewError
Raised when quality review encounters issues.

### Error Recovery

The system implements automatic fallback:

1. **CrewAI Mode** → **Direct Mode** → **Rule-based Processing**
2. **LLM Processing** → **Keyword Analysis**
3. **Full Processing** → **Partial Processing** → **Error Reporting**

---

## Examples

### Basic Usage

```python
from src.orchestration.crew_manager import FeedbackAnalysisCrew

# Initialize crew
crew = FeedbackAnalysisCrew(
    data_dir="data",
    confidence_threshold=0.8
)

# Process feedback
results = crew.process_feedback_data()

# Check results
print(f"Processed: {results['total_processed']} items")
print(f"Accuracy: {results['classification_accuracy']:.2%}")
```

### Individual Agent Usage

```python
from src.agents.feedback_classifier_agent import FeedbackClassifierAgent

# Initialize classifier
classifier = FeedbackClassifierAgent()

# Classify single feedback
result = classifier.classify_feedback("App crashes when I try to sync")
print(f"Category: {result['category']}")
print(f"Confidence: {result['confidence']}")
```

### Custom Configuration

```python
import os
from dotenv import load_dotenv

# Load custom environment
load_dotenv('custom.env')

# Initialize with custom settings
crew = FeedbackAnalysisCrew(
    data_dir=os.getenv('CUSTOM_DATA_DIR', 'data'),
    confidence_threshold=float(os.getenv('CONFIDENCE_THRESHOLD', 0.7))
)
```

---

## Performance Considerations

### Memory Usage
- Process data in batches for large datasets
- Monitor memory usage during task execution
- Use direct mode for memory-constrained environments

### API Rate Limits
- Monitor OpenAI API usage
- Implement rate limiting for large datasets
- Use caching for repeated classifications

### Processing Speed
- CrewAI Mode: ~10-12 items/second
- Direct Mode: ~12-15 items/second
- Rule-based fallback: ~50+ items/second

---

## Testing

### Unit Tests

```python
import unittest
from src.agents.feedback_classifier_agent import FeedbackClassifierAgent

class TestFeedbackClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = FeedbackClassifierAgent()
    
    def test_classify_bug(self):
        result = self.classifier.classify_feedback("App crashes")
        self.assertEqual(result['category'], 'Bug')
        self.assertGreater(result['confidence'], 0.5)
```

### Integration Tests

```python
def test_end_to_end_processing():
    crew = FeedbackAnalysisCrew()
    results = crew.process_feedback_data()
    assert results['status'] == 'success'
    assert results['total_processed'] > 0
```

---

## Migration Guide

### From Direct Processing to CrewAI

```python
# Before (direct)
system = FeedbackAnalysisSystem()
results = system.process_feedback()

# After (CrewAI)
crew = FeedbackAnalysisCrew()
results = crew.process_feedback_data()
```

### Custom Agent Integration

```python
# Create custom agent
from crewai import Agent

custom_agent = Agent(
    role='Custom Analyzer',
    goal='Perform custom analysis',
    backstory='Expert in custom analysis',
    tools=[custom_tool]
)

# Add to crew
crew.agents.append(custom_agent)
```
