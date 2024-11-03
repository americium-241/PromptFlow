# streamlit_logs.py

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ExecutionSession, ActionTrace, LogEntry
from database import Base
from collections import defaultdict
import datetime
import uuid
import streamlit_nested_layout

# Initialize database connection
engine = create_engine('sqlite:///logs.db')
SessionLocal = sessionmaker(bind=engine)

st.set_page_config(layout="wide")  # Set the layout to wide

st.title("Workflow Execution Logs")

# Set up sidebar filters
st.sidebar.header("Filters")

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

search_term = st.sidebar.text_input("Search Executions", "")
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
        
        # Prepare action trace options for filtering
        action_trace_options = {f"{trace.action_name} [{trace.trace_id}]": trace.trace_id for trace in action_traces}
        
        # Sidebar filters for action traces
        st.sidebar.subheader("Action Trace Filters")
        action_statuses = ["STARTED", "COMPLETED", "FAILED"]
        selected_statuses = st.sidebar.multiselect("Filter Actions by Status", action_statuses, default=action_statuses)
        action_search_term = st.sidebar.text_input("Search Actions", "")
        
        # Sidebar filters for log entries
        st.sidebar.subheader("Log Entry Filters")
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        selected_levels = st.sidebar.multiselect("Filter Logs by Level", log_levels, default=log_levels)
        
        # Create tabs
        tab1, tab2 = st.tabs(["Action Details", "Workflow Graph"])
        
        # -----------------------
        # Tab 1: Action Details with Logs
        # -----------------------
        with tab1:
            st.header("Action Details")
            
            if action_traces:
                # Build action tree
                def build_action_tree(traces):
                    tree = defaultdict(list)
                    for trace in traces:
                        tree[trace.parent_trace_id].append(trace)
                    return tree

                # Filter action traces
                filtered_traces = [trace for trace in action_traces if trace.status.name in selected_statuses]
                if action_search_term:
                    filtered_traces = [trace for trace in filtered_traces if action_search_term.lower() in trace.action_name.lower()]

                action_tree = build_action_tree(filtered_traces)

                # Display action details and logs
                def display_action_details(trace, tree, logs, selected_levels, level=0):
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
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Action Details
                            st.subheader("Action Details")
                            st.markdown(f"**Component**: `{trace.component}`")
                            st.markdown(f"**Action Name**: `{trace.action_name}`")
                            st.markdown(f"**Status**: <span style='color:{status_color}'>{trace.status.name}</span>", unsafe_allow_html=True)
                            st.write(f"**Start Time**: {trace.start_time}")
                            st.write(f"**End Time**: {trace.end_time}")
                            st.write(f"**Input Data**:")
                            st.json(trace.input_data)
                            st.write(f"**Output Data**:")
                            st.json(trace.output_data)
                        
                        with col2:
                            # Logs
                            st.subheader("Logs")
                            trace_logs = [log for log in logs if log.action_trace_id == trace.trace_id and log.level.name in selected_levels]
                            if trace_logs:
                                for log in trace_logs:
                                    log_color = {
                                        "DEBUG": "gray",
                                        "INFO": "blue",
                                        "WARNING": "orange",
                                        "ERROR": "red"
                                    }.get(log.level.name, "black")
                                    log_expander_label = f"{log.timestamp} - {log.level.name} - {log.component}"
                                    with st.expander(log_expander_label, expanded=False):
                                        st.markdown(f"**Component**: `{log.component}`")
                                        st.markdown(f"**Level**: <span style='color:{log_color}'>{log.level.name}</span>", unsafe_allow_html=True)
                                        st.write(f"**Timestamp**: {log.timestamp}")
                                        st.write(f"**Message**: {log.message}")
                                        if log.data:
                                            st.write(f"**Data**:")
                                            st.json(log.data)
                            else:
                                st.write("No logs for this action.")

                        # Display child actions
                        for child_trace in tree.get(trace.trace_id, []):
                            display_action_details(child_trace, tree, logs, selected_levels, level + 1)
                root_traces = action_tree[None]  # Actions with no parent_trace_id
                for root_trace in root_traces:
                    display_action_details(root_trace, action_tree, log_entries, selected_levels)
            else:
                st.write("No action traces found for this execution.")

        # --------------------
        # Tab 2: Workflow Graph
        # --------------------
        with tab2:
            st.header("Workflow Graph")

            if action_traces:
                # Build the graph
                import graphviz

                dot = graphviz.Digraph()
                dot.attr(compound='true')

                # Build action tree with depth information
                def build_action_tree_with_depth(traces, parent_id=None, depth=0, tree=None):
                    if tree is None:
                        tree = {}
                    for trace in traces:
                        if trace.parent_trace_id == parent_id:
                            tree[trace] = {'depth': depth, 'children': {}}
                            build_action_tree_with_depth(traces, trace.trace_id, depth + 1, tree[trace]['children'])
                    return tree

                action_tree = build_action_tree_with_depth(action_traces)

                # Function to add nodes and edges to the graph
                def add_nodes_edges(dot, tree, parent_id=None, depth=0):
                    for trace, info in tree.items():
                        with dot.subgraph(name=f"cluster_depth_{depth}") as sub:
                            sub.attr(rank='same')
                            node_label = f"{trace.action_name}\n{trace.trace_id[:8]}"
                            status_color = {
                                "COMPLETED": "green",
                                "FAILED": "red",
                                "STARTED": "orange"
                            }.get(trace.status.name, "black")
                            sub.node(trace.trace_id, label=node_label, color=status_color, shape='box', style='filled,rounded', fillcolor='white')

                        if parent_id:
                            dot.edge(parent_id, trace.trace_id)

                        # Recurse for children
                        add_nodes_edges(dot, info['children'], trace.trace_id, depth + 1)

                add_nodes_edges(dot, action_tree)

                st.graphviz_chart(dot)
            else:
                st.write("No action traces found for this execution.")
else:
    st.write("No executions found.")
