# app.py
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ExecutionSession, ActionTrace, LogEntry
from database import Base
from collections import defaultdict
import datetime
import graphviz
import uuid
import streamlit_nested_layout
# Initialize database connection
engine = create_engine('sqlite:///logs.db')
SessionLocal = sessionmaker(bind=engine)

st.set_page_config(layout="wide")  # Set the layout to wide

st.title("Workflow Execution Logs")

# Functions to retrieve data
def get_execution_sessions():
    session = SessionLocal()
    try:
        executions = session.query(ExecutionSession).order_by(ExecutionSession.start_time.desc()).all()
        return executions
    finally:
        session.close()

def get_action_traces(execution_id):
    session = SessionLocal()
    try:
        traces = session.query(ActionTrace).filter_by(execution_id=execution_id).order_by(ActionTrace.start_time).all()
        return traces
    finally:
        session.close()

def get_log_entries(execution_id):
    session = SessionLocal()
    try:
        logs = session.query(LogEntry).filter_by(execution_id=execution_id).order_by(LogEntry.timestamp).all()
        return logs
    finally:
        session.close()

# Main application
executions = get_execution_sessions()

search_term = st.text_input("Search Executions", "")
if search_term:
    executions = [exec for exec in executions if search_term.lower() in exec.execution_id.lower()]

if executions:
    execution_options = {f"{exec.execution_id} - {exec.start_time}": exec.execution_id for exec in executions}
    selected_execution = st.selectbox("Select an Execution Session", list(execution_options.keys()))
    
    if selected_execution:
        execution_id = execution_options[selected_execution]
        st.subheader(f"Execution ID: {execution_id}")
        
        action_traces = get_action_traces(execution_id)
        log_entries = get_log_entries(execution_id)
        
        # Create two columns
        col1, col2 = st.columns(2)
        
        # -----------------------
        # Column 1: Action Traces
        # -----------------------
        with col1:
            st.header("Action Traces")
            
            # Filter options for action traces
            action_statuses = ["STARTED", "COMPLETED", "FAILED"]
            selected_statuses = st.multiselect("Filter Actions by Status", action_statuses, default=action_statuses)
            action_search_term = st.text_input("Search Actions", "")
            
            if action_traces:
                # Filter action traces
                filtered_traces = [trace for trace in action_traces if trace.status.name in selected_statuses]
                if action_search_term:
                    filtered_traces = [trace for trace in filtered_traces if action_search_term.lower() in trace.action_name.lower()]
                
                # Build action tree
                # app.py

                def build_action_tree(traces):
                    tree = defaultdict(list)
                    for trace in traces:
                        tree[trace.parent_trace_id].append(trace)
                    return tree


                action_tree = build_action_tree(filtered_traces)
                
                # Build and display the graph using graphviz
                def build_graph_graphviz(tree, parent_id=None, dot=None):
                    if dot is None:
                        dot = graphviz.Digraph(format='png')
                    
                    children = tree.get(parent_id, [])
                    for child in children:
                        node_label = f"{child.action_name}\n[{child.status.name}]"
                        status_color = {
                            "COMPLETED": "green",
                            "FAILED": "red",
                            "STARTED": "orange"
                        }.get(child.status.name, "gray")
                        node_id = str(uuid.uuid4())
                        child._graphviz_id = node_id  # Assign a unique ID to the node
                        dot.node(node_id, label=node_label, color=status_color, style='filled', fillcolor='white')
                        if parent_id:
                            parent_trace = next((t for t in action_traces if t.trace_id == parent_id), None)
                            if parent_trace and hasattr(parent_trace, '_graphviz_id'):
                                dot.edge(parent_trace._graphviz_id, node_id)
                        build_graph_graphviz(tree, child.trace_id, dot)
                    return dot
                
                #dot = build_graph_graphviz(action_tree)
                #st.graphviz_chart(dot)
                
                # Optionally, display action details in expanders
                st.subheader("Action Details")
                def display_action_details(trace, tree, level=0):
                    status_color = {
                        "COMPLETED": "green",
                        "FAILED": "red",
                        "STARTED": "orange"
                    }.get(trace.status.name, "black")

                    duration = ""
                    if trace.end_time:
                        duration_sec = (trace.end_time - trace.start_time).total_seconds()
                        duration = f" - Duration: {duration_sec:.2f}s"

                    expander_label = f"{' ' * 2 * level}Action: {trace.action_name} [{trace.status.name}]{duration}"
                    with st.expander(expander_label, expanded=False):
                        st.markdown(f"**Component**: `{trace.component}`")
                        st.markdown(f"**Action Name**: `{trace.action_name}`")
                        st.markdown(f"**Status**: <span style='color:{status_color}'>{trace.status.name}</span>", unsafe_allow_html=True)
                        st.write(f"**Start Time**: {trace.start_time}")
                        st.write(f"**End Time**: {trace.end_time}")
                        st.write(f"**Input Data**:")
                        st.json(trace.input_data)
                        st.write(f"**Output Data**:")
                        st.json(trace.output_data)

                        # Display child actions
                        for child_trace in tree.get(trace.trace_id, []):
                            display_action_details(child_trace, tree, level + 1)

                
                root_traces = action_tree[None]  # Actions with no parent_trace_id
                for root_trace in root_traces:
                    display_action_details(root_trace, action_tree)
            else:
                st.write("No action traces found for this execution.")
        
        # --------------------
        # Column 2: Log Entries
        # --------------------
        with col2:
            st.header("Log Entries")
            
            # Option to filter logs by level
            log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
            selected_levels = st.multiselect("Filter Logs by Level", log_levels, default=log_levels)
            log_search_term = st.text_input("Search Logs", "")
            
            filtered_logs = [log for log in log_entries if log.level.name in selected_levels]
            if log_search_term:
                filtered_logs = [log for log in filtered_logs if log.message and log_search_term.lower() in log.message.lower()]
            
            for log in filtered_logs:
                log_color = {
                    "DEBUG": "gray",
                    "INFO": "blue",
                    "WARNING": "orange",
                    "ERROR": "red"
                }.get(log.level.name, "black")
                with st.expander(f"{log.timestamp} - {log.level.name} - {log.component}", expanded=False):
                    st.markdown(f"**Component**: `{log.component}`")
                    st.markdown(f"**Level**: <span style='color:{log_color}'>{log.level.name}</span>", unsafe_allow_html=True)
                    st.write(f"**Timestamp**: {log.timestamp}")
                    st.write(f"**Message**: {log.message}")
                    st.write(f"**Data**:")
                    st.json(log.data)
else:
    st.write("No executions found.")
