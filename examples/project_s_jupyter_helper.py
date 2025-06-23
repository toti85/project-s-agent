"""
Project-S Python Client - Jupyter Integration Example
----------------------------------------------------
This script demonstrates how to use the Project-S Python client within a Jupyter Notebook
for data analysis tasks. The client is used to interact with various Project-S API endpoints
and LangGraph workflows for enhanced data analysis capabilities.

To use this in a Jupyter notebook, you would:
1. Copy this code into a cell
2. Import the ProjectSNotebookHelper class
3. Initialize the helper and use its methods

Example:
    from project_s_jupyter_helper import ProjectSNotebookHelper
    helper = ProjectSNotebookHelper()
    helper.authenticate("admin", "password123")
    
    # Then call methods like:
    df = helper.analyze_dataset("my_data.csv")
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, HTML, JSON
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union, Callable
import logging
from project_s_python_client import ProjectSClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectSNotebookHelper:
    """
    Helper class for using Project-S in Jupyter notebooks
    """
    
    def __init__(self, base_url="http://localhost:8000"):
        """Initialize the helper with a Project-S client"""
        self.client = ProjectSClient(base_url)
        self.is_authenticated = False
        self.analysis_results = {}
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with the Project-S API"""
        result = self.client.authenticate(username, password)
        self.is_authenticated = result
        
        if result:
            display(HTML("<h3 style='color:green'>✅ Successfully authenticated with Project-S API</h3>"))
        else:
            display(HTML("<h3 style='color:red'>❌ Authentication failed</h3>"))
        
        return result
    
    def _check_auth(self):
        """Check if the client is authenticated"""
        if not self.is_authenticated:
            display(HTML("<h3 style='color:red'>❌ Not authenticated. Call authenticate() first</h3>"))
            raise ValueError("Not authenticated. Call authenticate() first")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get and display system information"""
        self._check_auth()
        
        try:
            info = self.client.get_system_status()
            
            # Display as HTML
            html = f"""
            <div style='background-color:#f5f5f5; padding:10px; border-radius:5px;'>
                <h3>Project-S System Information</h3>
                <ul>
                    <li><b>Status:</b> {info.get('status', 'Unknown')}</li>
                    <li><b>Version:</b> {info.get('version', 'Unknown')}</li>
                    <li><b>Services:</b> {len(info.get('services', []))} services running</li>
                    <li><b>Memory Usage:</b> {info.get('memory_usage', '0')} MB</li>
                    <li><b>Uptime:</b> {info.get('uptime', '0')} seconds</li>
                </ul>
            </div>
            """
            display(HTML(html))
            
            # Return the raw data for further processing
            return info
        
        except Exception as e:
            display(HTML(f"<h3 style='color:red'>❌ Error getting system info: {e}</h3>"))
            return {}
    
    def analyze_dataset(self, data_path: str, analysis_type: str = "exploratory") -> Optional[pd.DataFrame]:
        """
        Analyze a dataset using Project-S cognitive analysis
        
        Args:
            data_path: Path to the dataset (local or remote)
            analysis_type: Type of analysis to perform (exploratory, statistical, predictive)
            
        Returns:
            DataFrame with analysis results if successful
        """
        self._check_auth()
        
        try:
            # Create a workflow for dataset analysis
            workflow = self.client.create_workflow(
                name=f"Dataset Analysis - {data_path}",
                workflow_type="data_analysis",
                config={
                    "analysis_type": analysis_type,
                    "return_format": "dataframe"
                },
                initial_context={
                    "data_path": data_path,
                    "timestamp": time.time()
                }
            )
            
            workflow_id = workflow.get("id")
            display(HTML(f"<p>✅ Created analysis workflow: {workflow_id}</p>"))
            
            # Poll for workflow completion
            max_attempts = 30
            for attempt in range(max_attempts):
                status = self.client.get_workflow_status(workflow_id)
                current_status = status.get('status')
                
                if current_status == 'completed':
                    result = status.get('result', {})
                    self.analysis_results[workflow_id] = result
                    
                    # Try to convert the result to a DataFrame
                    if 'data' in result:
                        try:
                            df = pd.DataFrame(result['data'])
                            display(HTML(f"<h3>Analysis Complete: {result.get('summary', '')}</h3>"))
                            return df
                        except Exception as e:
                            display(HTML(f"<p>Note: Could not convert result to DataFrame: {e}</p>"))
                    
                    # Display the raw result
                    display(JSON(result))
                    return None
                
                elif current_status == 'failed':
                    display(HTML(f"<h3 style='color:red'>❌ Analysis failed: {status.get('error', 'Unknown error')}</h3>"))
                    return None
                
                elif current_status == 'waiting_for_decision':
                    # Handle pending decisions
                    pending_decisions = self.client.get_pending_decisions(workflow_id)
                    if pending_decisions:
                        display(HTML("<p>Workflow requires a decision. Automatically selecting first option...</p>"))
                        for decision in pending_decisions:
                            decision_point = decision.get('decision_point')
                            options = decision.get('options', [])
                            
                            if options:
                                selected_option = options[0]
                                self.client.make_workflow_decision(
                                    workflow_id=workflow_id,
                                    decision_point=decision_point,
                                    selected_option=selected_option
                                )
                
                # Display progress
                if attempt % 3 == 0:  # Update progress every 3 attempts
                    display(HTML(f"<p>⏳ Waiting for analysis to complete... (Status: {current_status})</p>"))
                
                time.sleep(2)
            
            display(HTML("<h3 style='color:red'>❌ Analysis timed out</h3>"))
            return None
        
        except Exception as e:
            display(HTML(f"<h3 style='color:red'>❌ Error analyzing dataset: {e}</h3>"))
            return None
    
    def visualize_data(self, df: pd.DataFrame, visualization_type: str = "auto") -> None:
        """
        Visualize a DataFrame using Project-S visualization recommendations
        
        Args:
            df: DataFrame to visualize
            visualization_type: Type of visualization or 'auto' for automatic selection
        """
        self._check_auth()
        
        try:
            # Use Project-S to get visualization recommendations
            query = f"Recommend visualization for dataframe with columns: {', '.join(df.columns)}"
            
            if visualization_type != "auto":
                query += f". Use visualization type: {visualization_type}"
            
            response = self.client.ask(query)
            recommendations = response.get('response', {}).get('recommendations', [])
            
            if not recommendations:
                # If no specific recommendations, create basic visualizations
                display(HTML("<h3>Basic Data Visualization</h3>"))
                
                # Display basic statistics
                display(HTML("<h4>Summary Statistics</h4>"))
                display(df.describe())
                
                # Create some basic plots based on data types
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                categorical_cols = df.select_dtypes(include=['object']).columns
                
                plt.figure(figsize=(12, 10))
                
                # Correlation heatmap for numeric columns
                if len(numeric_cols) > 1:
                    plt.subplot(2, 2, 1)
                    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm')
                    plt.title('Correlation Heatmap')
                
                # Histogram of first numeric column
                if len(numeric_cols) > 0:
                    plt.subplot(2, 2, 2)
                    sns.histplot(df[numeric_cols[0]], kde=True)
                    plt.title(f'Distribution of {numeric_cols[0]}')
                
                # Bar chart of first categorical column
                if len(categorical_cols) > 0:
                    plt.subplot(2, 2, 3)
                    df[categorical_cols[0]].value_counts().plot(kind='bar')
                    plt.title(f'Counts of {categorical_cols[0]}')
                
                # Scatter plot of first two numeric columns
                if len(numeric_cols) > 1:
                    plt.subplot(2, 2, 4)
                    sns.scatterplot(x=df[numeric_cols[0]], y=df[numeric_cols[1]])
                    plt.title(f'{numeric_cols[0]} vs {numeric_cols[1]}')
                
                plt.tight_layout()
                plt.show()
            
            else:
                # Implement the recommended visualizations
                display(HTML("<h3>Project-S Recommended Visualizations</h3>"))
                
                for i, rec in enumerate(recommendations):
                    chart_type = rec.get('chart_type')
                    columns = rec.get('columns', [])
                    title = rec.get('title', f'Visualization {i+1}')
                    
                    display(HTML(f"<h4>{title}</h4>"))
                    display(HTML(f"<p><i>{rec.get('explanation', '')}</i></p>"))
                    
                    if not columns or not all(col in df.columns for col in columns):
                        display(HTML("<p>⚠️ Some recommended columns not found in DataFrame</p>"))
                        continue
                    
                    plt.figure(figsize=(10, 6))
                    
                    if chart_type == 'bar':
                        df[columns].plot(kind='bar')
                    elif chart_type == 'histogram':
                        df[columns[0]].plot(kind='hist', bins=20)
                    elif chart_type == 'scatter':
                        if len(columns) >= 2:
                            plt.scatter(df[columns[0]], df[columns[1]])
                            plt.xlabel(columns[0])
                            plt.ylabel(columns[1])
                    elif chart_type == 'line':
                        df[columns].plot(kind='line')
                    elif chart_type == 'heatmap':
                        sns.heatmap(df[columns].corr(), annot=True, cmap='coolwarm')
                    elif chart_type == 'pie':
                        df[columns[0]].value_counts().plot(kind='pie', autopct='%1.1f%%')
                    elif chart_type == 'box':
                        df[columns].plot(kind='box')
                    else:
                        display(HTML(f"<p>⚠️ Unsupported chart type: {chart_type}</p>"))
                        continue
                    
                    plt.title(title)
                    plt.tight_layout()
                    plt.show()
        
        except Exception as e:
            display(HTML(f"<h3 style='color:red'>❌ Error visualizing data: {e}</h3>"))
    
    def analyze_text(self, text: str, analysis_type: str = "sentiment") -> Dict[str, Any]:
        """
        Analyze text using Project-S cognitive capabilities
        
        Args:
            text: The text to analyze
            analysis_type: Type of analysis (sentiment, entity, keyword, summary)
            
        Returns:
            Dict containing analysis results
        """
        self._check_auth()
        
        try:
            # Use ASK command for text analysis
            query = f"Perform {analysis_type} analysis on the following text: {text}"
            response = self.client.ask(query)
            
            # Extract and format the results
            result = response.get('response', {})
            
            # Display results with appropriate formatting
            if analysis_type == 'sentiment':
                sentiment = result.get('sentiment', 'neutral')
                score = result.get('score', 0.0)
                
                # Create a visual representation of sentiment
                color = 'green' if sentiment == 'positive' else ('red' if sentiment == 'negative' else 'gray')
                html = f"""
                <div style='background-color:#f5f5f5; padding:15px; border-radius:5px;'>
                    <h3>Sentiment Analysis Results</h3>
                    <p><b>Text:</b> <i>{text[:100]}{'...' if len(text) > 100 else ''}</i></p>
                    <p><b>Sentiment:</b> <span style='color:{color};'>{sentiment.upper()}</span></p>
                    <p><b>Confidence Score:</b> {score:.2f}</p>
                    <div style='width:100%; background-color:#ddd; height:20px; border-radius:10px;'>
                        <div style='width:{abs(score)*100:.1f}%; background-color:{color}; height:20px; border-radius:10px;'></div>
                    </div>
                </div>
                """
                display(HTML(html))
            
            elif analysis_type == 'entity':
                entities = result.get('entities', [])
                
                html = f"""
                <div style='background-color:#f5f5f5; padding:15px; border-radius:5px;'>
                    <h3>Entity Analysis Results</h3>
                    <p><b>Text:</b> <i>{text[:100]}{'...' if len(text) > 100 else ''}</i></p>
                    <p><b>Entities Found:</b> {len(entities)}</p>
                    <table style='width:100%; border-collapse:collapse;'>
                        <tr style='background-color:#ddd;'>
                            <th style='padding:8px; text-align:left; border:1px solid #ccc;'>Entity</th>
                            <th style='padding:8px; text-align:left; border:1px solid #ccc;'>Type</th>
                            <th style='padding:8px; text-align:left; border:1px solid #ccc;'>Confidence</th>
                        </tr>
                """
                
                for entity in entities:
                    html += f"""
                        <tr>
                            <td style='padding:8px; border:1px solid #ccc;'>{entity.get('text', '')}</td>
                            <td style='padding:8px; border:1px solid #ccc;'>{entity.get('type', '')}</td>
                            <td style='padding:8px; border:1px solid #ccc;'>{entity.get('confidence', 0.0):.2f}</td>
                        </tr>
                    """
                
                html += """
                    </table>
                </div>
                """
                display(HTML(html))
            
            elif analysis_type == 'summary':
                summary = result.get('summary', '')
                
                html = f"""
                <div style='background-color:#f5f5f5; padding:15px; border-radius:5px;'>
                    <h3>Text Summarization Results</h3>
                    <p><b>Original Text:</b> <i>{text[:100]}{'...' if len(text) > 100 else ''}</i></p>
                    <p><b>Original Length:</b> {len(text)} characters</p>
                    <p><b>Summary Length:</b> {len(summary)} characters</p>
                    <div style='background-color:#fff; padding:10px; border-left:4px solid #333;'>
                        <p><b>Summary:</b> {summary}</p>
                    </div>
                </div>
                """
                display(HTML(html))
            
            else:
                # Generic display for other analysis types
                display(HTML("<h3>Analysis Results</h3>"))
                display(JSON(result))
            
            return result
        
        except Exception as e:
            display(HTML(f"<h3 style='color:red'>❌ Error analyzing text: {e}</h3>"))
            return {}
    
    def run_decision_analysis(self, question: str, options: List[str] = None) -> Dict[str, Any]:
        """
        Run a decision analysis workflow
        
        Args:
            question: The decision question to analyze
            options: List of options to evaluate (if None, the system will generate options)
            
        Returns:
            Dict containing decision analysis results
        """
        self._check_auth()
        
        try:
            # Create initial context for decision analysis
            initial_context = {
                "question": question,
                "timestamp": time.time()
            }
            
            if options:
                initial_context["options"] = options
            
            # Create a workflow for decision analysis
            workflow = self.client.create_workflow(
                name=f"Decision Analysis - {question[:30]}...",
                workflow_type="decision_analysis",
                config={
                    "max_depth": 3,
                    "evaluation_criteria": ["feasibility", "impact", "cost", "risk"]
                },
                initial_context=initial_context
            )
            
            workflow_id = workflow.get("id")
            display(HTML(f"<p>✅ Created decision analysis workflow: {workflow_id}</p>"))
            
            # Poll for workflow completion
            max_attempts = 30
            for attempt in range(max_attempts):
                status = self.client.get_workflow_status(workflow_id)
                current_status = status.get('status')
                
                if current_status == 'completed':
                    result = status.get('result', {})
                    
                    # Display the results in a visual format
                    analyzed_options = result.get('analyzed_options', [])
                    recommendation = result.get('recommendation', {})
                    
                    html = f"""
                    <div style='background-color:#f5f5f5; padding:15px; border-radius:5px;'>
                        <h3>Decision Analysis Results</h3>
                        <p><b>Question:</b> {question}</p>
                        <p><b>Recommended Option:</b> {recommendation.get('option', 'No recommendation')}</p>
                        <p><b>Confidence:</b> {recommendation.get('confidence', 0)*100:.1f}%</p>
                        <p><b>Reasoning:</b> {recommendation.get('reasoning', 'No reasoning provided')}</p>
                        
                        <h4>Option Evaluation</h4>
                        <table style='width:100%; border-collapse:collapse;'>
                            <tr style='background-color:#ddd;'>
                                <th style='padding:8px; text-align:left; border:1px solid #ccc;'>Option</th>
                                <th style='padding:8px; text-align:left; border:1px solid #ccc;'>Pros</th>
                                <th style='padding:8px; text-align:left; border:1px solid #ccc;'>Cons</th>
                                <th style='padding:8px; text-align:left; border:1px solid #ccc;'>Score</th>
                            </tr>
                    """
                    
                    for option in analyzed_options:
                        option_name = option.get('name', '')
                        pros = option.get('pros', [])
                        cons = option.get('cons', [])
                        score = option.get('score', 0)
                        
                        # Determine background color based on whether this is the recommended option
                        bg_color = '#e6f7e6' if option_name == recommendation.get('option') else '#fff'
                        
                        html += f"""
                            <tr style='background-color:{bg_color};'>
                                <td style='padding:8px; border:1px solid #ccc;'><b>{option_name}</b></td>
                                <td style='padding:8px; border:1px solid #ccc;'>
                                    <ul>
                        """
                        
                        for pro in pros:
                            html += f"<li>{pro}</li>"
                        
                        html += """
                                    </ul>
                                </td>
                                <td style='padding:8px; border:1px solid #ccc;'>
                                    <ul>
                        """
                        
                        for con in cons:
                            html += f"<li>{con}</li>"
                        
                        html += f"""
                                    </ul>
                                </td>
                                <td style='padding:8px; border:1px solid #ccc;'>{score:.2f}</td>
                            </tr>
                        """
                    
                    html += """
                        </table>
                    </div>
                    """
                    
                    display(HTML(html))
                    
                    # Create a bar chart of option scores
                    option_names = [option.get('name', f'Option {i}') for i, option in enumerate(analyzed_options)]
                    option_scores = [option.get('score', 0) for option in analyzed_options]
                    
                    plt.figure(figsize=(10, 6))
                    bars = plt.bar(option_names, option_scores, color=['green' if name == recommendation.get('option') else 'blue' for name in option_names])
                    plt.xlabel('Options')
                    plt.ylabel('Score')
                    plt.title('Option Evaluation Scores')
                    plt.xticks(rotation=45, ha='right')
                    
                    # Add values on top of bars
                    for bar in bars:
                        height = bar.get_height()
                        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                                f'{height:.2f}', ha='center', va='bottom')
                    
                    plt.tight_layout()
                    plt.show()
                    
                    return result
                
                elif current_status == 'failed':
                    display(HTML(f"<h3 style='color:red'>❌ Decision analysis failed: {status.get('error', 'Unknown error')}</h3>"))
                    return {}
                
                # Display progress
                if attempt % 3 == 0:
                    display(HTML(f"<p>⏳ Analyzing decision... (Status: {current_status})</p>"))
                
                time.sleep(2)
            
            display(HTML("<h3 style='color:red'>❌ Decision analysis timed out</h3>"))
            return {}
        
        except Exception as e:
            display(HTML(f"<h3 style='color:red'>❌ Error in decision analysis: {e}</h3>"))
            return {}


# Example of how to use this in a Jupyter Notebook
"""
# Example Jupyter Notebook Usage

from project_s_jupyter_helper import ProjectSNotebookHelper

# Initialize the helper
helper = ProjectSNotebookHelper()

# Authenticate with Project-S
helper.authenticate("admin", "password123")

# Get system info
system_info = helper.get_system_info()

# Create a sample DataFrame
import pandas as pd
import numpy as np

# Sample data
data = {
    'category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A'],
    'value': np.random.randint(1, 100, 10),
    'metric': np.random.normal(50, 15, 10)
}
df = pd.DataFrame(data)

# Visualize the data
helper.visualize_data(df)

# Analyze text
text_result = helper.analyze_text(
    "Project-S is an innovative hybrid system that combines multiple AI models for enhanced decision making.",
    analysis_type="sentiment"
)

# Run decision analysis
decision_result = helper.run_decision_analysis(
    "Which machine learning model should we use for sentiment analysis?",
    options=["BERT", "RoBERTa", "DistilBERT", "Traditional ML with TF-IDF"]
)
"""
