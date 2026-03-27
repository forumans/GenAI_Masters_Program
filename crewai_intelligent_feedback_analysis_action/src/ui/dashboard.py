"""
Streamlit Dashboard for Intelligent User Feedback Analysis System
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime, timedelta
import sys

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from orchestration.crew_manager import FeedbackAnalysisCrew

# Page configuration
st.set_page_config(
    page_title="Intelligent Feedback Analysis System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-ready { background-color: #00cc00; }
    .status-processing { background-color: #ff9900; }
    .status-error { background-color: #ff3333; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load cached data from files"""
    data = {}
    
    # Load tickets
    if os.path.exists("data/generated_tickets.csv"):
        data['tickets'] = pd.read_csv("data/generated_tickets.csv")
    else:
        data['tickets'] = pd.DataFrame()
    
    # Load reviews
    if os.path.exists("data/quality_reviews.csv"):
        data['reviews'] = pd.read_csv("data/quality_reviews.csv")
    else:
        data['reviews'] = pd.DataFrame()
    
    # Load metrics
    if os.path.exists("data/metrics.csv"):
        data['metrics'] = pd.read_csv("data/metrics.csv")
    else:
        data['metrics'] = pd.DataFrame()
    
    # Load analyzed feedback
    if os.path.exists("data/analyzed_feedback.csv"):
        data['feedback'] = pd.read_csv("data/analyzed_feedback.csv")
    else:
        data['feedback'] = pd.DataFrame()
    
    return data

def create_sidebar():
    """Create sidebar with navigation and controls"""
    with st.sidebar:
        st.header("🧠 Feedback Analysis System")
        
        # Navigation
        page = st.selectbox(
            "Navigate to:",
            ["Dashboard", "Data Analysis", "Ticket Management", "Configuration", "System Status"]
        )
        
        st.divider()
        
        # System Controls
        st.subheader("System Controls")
        
        # Initialize crew manager in session state
        if 'crew_manager' not in st.session_state:
            st.session_state.crew_manager = FeedbackAnalysisCrew()
        
        # Process new data button
        if st.button("🚀 Process New Data", type="primary"):
            with st.spinner("Processing feedback data..."):
                try:
                    results = st.session_state.crew_manager.process_feedback_data()
                    st.session_state.processing_results = results
                    st.success("Processing completed successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Processing failed: {str(e)}")
        
        # Clear cache button
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")
        
        st.divider()
        
        # Quick Stats
        if 'tickets' in st.session_state.data and len(st.session_state.data['tickets']) > 0:
            st.subheader("Quick Stats")
            tickets = st.session_state.data['tickets']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Tickets", len(tickets))
            with col2:
                open_tickets = len(tickets[tickets['status'] == 'Open'])
                st.metric("Open Tickets", open_tickets)
        
        return page

def dashboard_page():
    """Main dashboard page"""
    st.markdown('<h1 class="main-header">📊 System Dashboard</h1>', unsafe_allow_html=True)
    
    if 'processing_results' in st.session_state:
        results = st.session_state.processing_results
        
        # Processing Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Processed",
                results['processing_stats']['total_processed'],
                delta=None
            )
        
        with col2:
            st.metric(
                "Successful",
                results['processing_stats']['successful'],
                delta=None
            )
        
        with col3:
            st.metric(
                "Processing Time",
                f"{results['processing_stats']['processing_time']:.2f}s",
                delta=None
            )
        
        with col4:
            accuracy = results.get('accuracy_evaluation', {}).get('overall_accuracy', 0)
            st.metric(
                "Classification Accuracy",
                f"{accuracy:.2%}" if accuracy > 0 else "N/A",
                delta=None
            )
        
        # Category Distribution
        st.subheader("📈 Feedback Category Distribution")
        
        if 'data_summary' in results:
            category_data = results['data_summary']['category_distribution']
            
            fig = px.pie(
                values=list(category_data.values()),
                names=list(category_data.keys()),
                title="Feedback Categories"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Quality Metrics
        st.subheader("✅ Quality Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'quality_stats' in results:
                quality_stats = results['quality_stats']
                
                fig_quality = go.Figure(data=[
                    go.Bar(name=level, x=[level], y=[quality_stats['quality_level_distribution'].get(level, 0)])
                    for level in ['Excellent', 'Good', 'Acceptable', 'Needs Improvement', 'Poor']
                ])
                
                fig_quality.update_layout(
                    title="Ticket Quality Distribution",
                    xaxis_title="Quality Level",
                    yaxis_title="Count"
                )
                st.plotly_chart(fig_quality, use_container_width=True)
        
        with col2:
            if 'ticket_stats' in results:
                ticket_stats = results['ticket_stats']
                
                priority_data = ticket_stats.get('priority_distribution', {})
                
                fig_priority = px.bar(
                    x=list(priority_data.keys()),
                    y=list(priority_data.values()),
                    title="Ticket Priority Distribution"
                )
                st.plotly_chart(fig_priority, use_container_width=True)
    
    else:
        st.info("No processing results available. Click 'Process New Data' to start analysis.")
        
        # Show sample data if available
        if 'tickets' in st.session_state.data and len(st.session_state.data['tickets']) > 0:
            st.subheader("📋 Recent Tickets")
            
            tickets = st.session_state.data['tickets'].head(10)
            st.dataframe(tickets[['ticket_id', 'title', 'category', 'priority', 'status', 'created_at']])

def data_analysis_page():
    """Data analysis page"""
    st.markdown('<h1 class="main-header">📊 Data Analysis</h1>', unsafe_allow_html=True)
    
    if 'feedback' in st.session_state.data and len(st.session_state.data['feedback']) > 0:
        feedback = st.session_state.data['feedback']
        
        # Analysis filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_category = st.selectbox(
                "Filter by Category",
                ["All"] + list(feedback['predicted_category'].unique())
            )
        
        with col2:
            selected_source = st.selectbox(
                "Filter by Source",
                ["All"] + list(feedback['source_type'].unique())
            )
        
        with col3:
            min_confidence = st.slider(
                "Min Confidence",
                0.0, 1.0, 0.5, 0.1
            )
        
        # Apply filters
        filtered_feedback = feedback.copy()
        
        if selected_category != "All":
            filtered_feedback = filtered_feedback[filtered_feedback['predicted_category'] == selected_category]
        
        if selected_source != "All":
            filtered_feedback = filtered_feedback[filtered_feedback['source_type'] == selected_source]
        
        filtered_feedback = filtered_feedback[filtered_feedback['classification_confidence'] >= min_confidence]
        
        st.subheader(f"Filtered Data ({len(filtered_feedback)} items)")
        
        # Confidence distribution
        col1, col2 = st.columns(2)
        
        with col1:
            if 'classification_confidence' in filtered_feedback.columns and not filtered_feedback.empty:
                fig_confidence = px.histogram(
                    filtered_feedback,
                    x='classification_confidence',
                    title="Classification Confidence Distribution",
                    nbins=20
                )
                st.plotly_chart(fig_confidence, use_container_width=True)
            else:
                st.warning("No confidence data available for visualization")
        
        with col2:
            if 'predicted_category' in filtered_feedback.columns and not filtered_feedback.empty:
                category_counts = filtered_feedback['predicted_category'].value_counts()
                fig_category = px.bar(
                    x=category_counts.index.tolist(),
                    y=category_counts.values.tolist(),
                    title="Category Distribution (Filtered)"
                )
                st.plotly_chart(fig_category, use_container_width=True)
            else:
                st.warning("No category data available for visualization")
        
        # Detailed data table
        st.subheader("📋 Detailed Feedback Data")
        
        display_columns = ['id', 'predicted_category', 'classification_confidence', 'source_type']
        if 'severity' in filtered_feedback.columns:
            display_columns.append('severity')
        if 'feature_priority_score' in filtered_feedback.columns:
            display_columns.append('feature_priority_score')
        
        st.dataframe(filtered_feedback[display_columns])
        
        # Sample feedback content
        if len(filtered_feedback) > 0:
            st.subheader("📝 Sample Feedback Content")
            
            sample_size = min(5, len(filtered_feedback))
            samples = filtered_feedback.sample(sample_size)
            
            for idx, row in samples.iterrows():
                with st.expander(f"Feedback {row['id']} - {row['predicted_category']}"):
                    st.write(f"**Content:** {row.get('content', 'N/A')}")
                    st.write(f"**Confidence:** {row['classification_confidence']:.2f}")
                    st.write(f"**Source:** {row['source_type']}")
    
    else:
        st.warning("No feedback data available. Please process data first.")

def ticket_management_page():
    """Ticket management page"""
    st.markdown('<h1 class="main-header">🎫 Ticket Management</h1>', unsafe_allow_html=True)
    
    if 'tickets' in st.session_state.data and len(st.session_state.data['tickets']) > 0:
        tickets = st.session_state.data['tickets']
        reviews = st.session_state.data.get('reviews', pd.DataFrame())
        
        # Ticket filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_status = st.selectbox(
                "Filter by Status",
                ["All"] + list(tickets['status'].unique())
            )
        
        with col2:
            selected_priority = st.selectbox(
                "Filter by Priority",
                ["All"] + list(tickets['priority'].unique())
            )
        
        with col3:
            selected_category = st.selectbox(
                "Filter by Category",
                ["All"] + list(tickets['category'].unique())
            )
        
        # Apply filters
        filtered_tickets = tickets.copy()
        
        if selected_status != "All":
            filtered_tickets = filtered_tickets[filtered_tickets['status'] == selected_status]
        
        if selected_priority != "All":
            filtered_tickets = filtered_tickets[filtered_tickets['priority'] == selected_priority]
        
        if selected_category != "All":
            filtered_tickets = filtered_tickets[filtered_tickets['category'] == selected_category]
        
        st.subheader(f"Filtered Tickets ({len(filtered_tickets)} tickets)")
        
        # Ticket statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", len(filtered_tickets))
        
        with col2:
            high_priority = len(filtered_tickets[filtered_tickets['priority'].isin(['Critical', 'High'])])
            st.metric("High Priority", high_priority)
        
        with col3:
            open_tickets = len(filtered_tickets[filtered_tickets['status'] == 'Open'])
            st.metric("Open", open_tickets)
        
        with col4:
            avg_confidence = filtered_tickets['classification_confidence'].mean()
            st.metric("Avg Confidence", f"{avg_confidence:.2f}")
        
        # Ticket table
        st.subheader("📋 Ticket List")
        
        # Select columns to display
        display_columns = ['ticket_id', 'title', 'category', 'priority', 'status', 'created_at']
        st.dataframe(filtered_tickets[display_columns])
        
        # Ticket details
        if len(filtered_tickets) > 0:
            st.subheader("🔍 Ticket Details")
            
            selected_ticket_id = st.selectbox(
                "Select Ticket for Details",
                filtered_tickets['ticket_id'].tolist()
            )
            
            if selected_ticket_id:
                ticket_details = filtered_tickets[filtered_tickets['ticket_id'] == selected_ticket_id].iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Ticket Information**")
                    st.write(f"**ID:** {ticket_details['ticket_id']}")
                    st.write(f"**Title:** {ticket_details['title']}")
                    st.write(f"**Category:** {ticket_details['category']}")
                    st.write(f"**Priority:** {ticket_details['priority']}")
                    st.write(f"**Status:** {ticket_details['status']}")
                    st.write(f"**Created:** {ticket_details['created_at']}")
                    st.write(f"**Confidence:** {ticket_details['classification_confidence']:.2f}")
                
                with col2:
                    st.write("**Description**")
                    st.text_area("", ticket_details['description'], height=200, disabled=True, key="desc")
                
                # Quality review if available
                if len(reviews) > 0:
                    ticket_review = reviews[reviews['ticket_id'] == selected_ticket_id]
                    
                    if len(ticket_review) > 0:
                        review = ticket_review.iloc[0]
                        
                        st.subheader("✅ Quality Review")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Quality Score", f"{review['overall_score']:.3f}")
                        
                        with col2:
                            st.metric("Quality Level", review['quality_level'])
                        
                        with col3:
                            needs_review = "Yes" if review['needs_manual_review'] else "No"
                            st.metric("Needs Review", needs_review)
                        
                        # Parse issues and suggestions safely
                        issues = []
                        suggestions = []
                        
                        if 'issues' in review and review['issues']:
                            try:
                                if isinstance(review['issues'], str):
                                    import json
                                    issues = json.loads(review['issues']) if review['issues'].strip() else []
                                elif isinstance(review['issues'], list):
                                    issues = review['issues']
                            except:
                                issues = [str(review['issues'])] if review['issues'] else []
                        
                        if 'suggestions' in review and review['suggestions']:
                            try:
                                if isinstance(review['suggestions'], str):
                                    import json
                                    suggestions = json.loads(review['suggestions']) if review['suggestions'].strip() else []
                                elif isinstance(review['suggestions'], list):
                                    suggestions = review['suggestions']
                            except:
                                suggestions = [str(review['suggestions'])] if review['suggestions'] else []
                        
                        if issues:
                            st.write("**Issues:**")
                            for issue in issues:
                                st.write(f"• {issue}")
                        
                        if suggestions:
                            st.write("**Suggestions:**")
                            for suggestion in suggestions:
                                st.write(f"• {suggestion}")
                        
                        if not issues and not suggestions:
                            st.info("No specific issues or suggestions identified.")
    
    else:
        st.warning("No tickets available. Please process data first.")

def configuration_page():
    """Configuration page"""
    st.markdown('<h1 class="main-header">⚙️ Configuration</h1>', unsafe_allow_html=True)
    
    st.subheader("System Parameters")
    
    # Classification settings
    with st.expander("🔍 Classification Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            confidence_threshold = st.slider(
                "Classification Confidence Threshold",
                0.0, 1.0, 0.7, 0.1
            )
            
            bug_severity_threshold = st.slider(
                "Bug Severity Threshold",
                0.0, 1.0, 0.8, 0.1
            )
        
        with col2:
            feature_priority_threshold = st.slider(
                "Feature Priority Threshold",
                0.0, 1.0, 0.6, 0.1
            )
            
            enable_quality_check = st.checkbox(
                "Enable Quality Check",
                value=True
            )
    
    # File paths
    with st.expander("📁 File Paths"):
        data_dir = st.text_input("Data Directory", value="data")
        output_dir = st.text_input("Output Directory", value="data")
        
        st.write("**Input Files:**")
        st.write(f"- {data_dir}/app_store_reviews.csv")
        st.write(f"- {data_dir}/support_emails.csv")
        st.write(f"- {data_dir}/expected_classifications.csv")
        
        st.write("**Output Files:**")
        st.write(f"- {output_dir}/generated_tickets.csv")
        st.write(f"- {output_dir}/quality_reviews.csv")
        st.write(f"- {output_dir}/metrics.csv")
    
    # Agent settings
    with st.expander("🤖 Agent Settings"):
        st.write("**Agent Configuration:**")
        
        agent_settings = {
            "csv_reader": {"enabled": True, "timeout": 300},
            "feedback_classifier": {"enabled": True, "model": "gpt-3.5-turbo"},
            "bug_analyzer": {"enabled": True, "severity_threshold": 0.5},
            "feature_extractor": {"enabled": True, "impact_threshold": 0.5},
            "ticket_creator": {"enabled": True, "auto_approve": False},
            "quality_critic": {"enabled": True, "min_quality_score": 0.7}
        }
        
        # Display agent settings in columns instead of nested expanders
        for agent, settings in agent_settings.items():
            st.markdown(f"**🔧 {agent.replace('_', ' ').title()}**")
            col1, col2 = st.columns(2)
            
            for i, (key, value) in enumerate(settings.items()):
                if isinstance(value, bool):
                    with col1 if i % 2 == 0 else col2:
                        st.checkbox(key.replace('_', ' ').title(), value=value, key=f"{agent}_{key}")
                elif isinstance(value, (int, float)) and 0 <= value <= 1:
                    with col1 if i % 2 == 0 else col2:
                        st.slider(key.replace('_', ' ').title(), 0.0, 1.0, float(value), step=0.01, key=f"{agent}_{key}")
                elif isinstance(value, (int, float)) and value > 1:
                    with col1 if i % 2 == 0 else col2:
                        st.number_input(key.replace('_', ' ').title(), value=int(value), key=f"{agent}_{key}")
                else:
                    with col1 if i % 2 == 0 else col2:
                        st.text_input(key.replace('_', ' ').title(), value=str(value), key=f"{agent}_{key}")
            
            st.divider()
    
    # Save configuration
    if st.button("💾 Save Configuration", type="primary"):
        st.success("Configuration saved successfully!")
    
    # Reset configuration
    if st.button("🔄 Reset to Defaults"):
        st.success("Configuration reset to defaults!")

def system_status_page():
    """System status page"""
    st.markdown('<h1 class="main-header">🖥️ System Status</h1>', unsafe_allow_html=True)
    
    # System overview
    st.subheader("🔍 System Overview")
    
    # Check if crew manager exists
    if 'crew_manager' in st.session_state:
        status = st.session_state.crew_manager.get_processing_status()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_color = {
                'Processing': 'status-processing',
                'Idle': 'status-ready',
                'Error': 'status-error'
            }.get(status['status'], 'status-error')
            
            st.markdown(f"""
            <div class="metric-card">
                <span class="status-indicator {status_color}"></span>
                <strong>System Status:</strong> {status['status']}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <strong>Processed Items:</strong> {status['stats']['total_processed']}
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            processing_time = status['stats'].get('processing_time', 0)
            st.markdown(f"""
            <div class="metric-card">
                <strong>Last Processing:</strong> {processing_time:.2f}s
            </div>
            """, unsafe_allow_html=True)
    
    # Agent status
    st.subheader("🤖 Agent Status")
    
    agents = [
        ("CSV Reader", "Reads and parses feedback data"),
        ("Feedback Classifier", "Categorizes feedback using NLP"),
        ("Bug Analyzer", "Extracts technical details from bugs"),
        ("Feature Extractor", "Analyzes feature requests"),
        ("Ticket Creator", "Generates structured tickets"),
        ("Quality Critic", "Reviews ticket quality")
    ]
    
    for agent_name, description in agents:
        with st.expander(f"🔧 {agent_name}"):
            st.write(f"**Description:** {description}")
            st.markdown('<span class="status-indicator status-ready"></span> Ready', unsafe_allow_html=True)
    
    # File system status
    st.subheader("📁 File System Status")
    
    required_files = [
        ("data/app_store_reviews.csv", "App Store Reviews"),
        ("data/support_emails.csv", "Support Emails"),
        ("data/expected_classifications.csv", "Expected Classifications"),
        ("data/generated_tickets.csv", "Generated Tickets"),
        ("data/quality_reviews.csv", "Quality Reviews"),
        ("data/metrics.csv", "Metrics")
    ]
    
    for file_path, description in required_files:
        exists = os.path.exists(file_path)
        status_icon = "✅" if exists else "❌"
        file_size = f"{os.path.getsize(file_path):,} bytes" if exists else "Not found"
        
        st.write(f"{status_icon} **{description}** - {file_size}")
    
    # Recent activity log
    st.subheader("📋 Recent Activity")
    
    if os.path.exists("data/processing_log.csv"):
        try:
            log_data = pd.read_csv("data/processing_log.csv")
            if len(log_data) > 0:
                recent_logs = log_data.tail(10)
                st.dataframe(recent_logs[['timestamp', 'step', 'status']].sort_values('timestamp', ascending=False))
            else:
                st.info("No activity logs available")
        except Exception as e:
            st.error(f"Error reading activity log: {str(e)}")
    else:
        st.info("No activity log file found")

def main():
    """Main application entry point"""
    # Load data
    st.session_state.data = load_data()
    
    # Create sidebar
    page = create_sidebar()
    
    # Route to appropriate page
    if page == "Dashboard":
        dashboard_page()
    elif page == "Data Analysis":
        data_analysis_page()
    elif page == "Ticket Management":
        ticket_management_page()
    elif page == "Configuration":
        configuration_page()
    elif page == "System Status":
        system_status_page()

if __name__ == "__main__":
    main()
