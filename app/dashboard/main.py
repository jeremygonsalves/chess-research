"""Streamlit dashboard for chess evaluation platform."""

import json
import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# MUST be the first Streamlit command
st.set_page_config(
    page_title="Chess Evaluation Platform",
    page_icon="♟️",
    layout="wide",
)

# Configuration
API_BASE_URL = st.sidebar.text_input(
    "API Base URL", value="http://localhost:8000/api/v1"
)

st.title("♟️ Distributed Chess Engine Evaluation Platform")
st.markdown("Monitor and manage chess position evaluations across distributed workers.")


# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.selectbox(
    "Choose a page",
    ["Dashboard", "Submit Evaluation", "Task Status", "Engine Status"],
)


def get_health():
    """Get API health status."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None


def get_engines_health():
    """Get engine health status."""
    try:
        response = requests.get(f"{API_BASE_URL}/health/engines", timeout=5)
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None


def get_task_stats():
    """Get task queue statistics."""
    try:
        response = requests.get(f"{API_BASE_URL}/tasks/stats", timeout=5)
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None


def submit_evaluation(fen, engine, depth, time_limit):
    """Submit an evaluation task."""
    try:
        payload = {
            "fen": fen,
            "engine": engine,
            "depth": depth,
        }
        if time_limit:
            payload["time_limit"] = time_limit

        response = requests.post(
            f"{API_BASE_URL}/evaluate", json=payload, timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error submitting evaluation: {str(e)}")
        return None


def get_task_status(task_id):
    """Get status of a task."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/evaluate/{task_id}", timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None


# Dashboard Page
if page == "Dashboard":
    st.header("📊 System Dashboard")

    # System Status
    col1, col2, col3 = st.columns(3)

    with col1:
        health = get_health()
        if health:
            st.metric("API Status", "🟢 Healthy" if health.get("status") == "healthy" else "🔴 Unhealthy")
        else:
            st.metric("API Status", "🔴 Offline")

    with col2:
        task_stats = get_task_stats()
        if task_stats:
            st.metric("Active Tasks", task_stats.get("active_tasks", 0))
        else:
            st.metric("Active Tasks", "N/A")

    with col3:
        if task_stats:
            st.metric("Workers", len(task_stats.get("workers", [])))
        else:
            st.metric("Workers", "N/A")

    # Task Queue Statistics
    if task_stats:
        st.subheader("Task Queue Statistics")
        queue_data = {
            "Metric": ["Active", "Scheduled", "Reserved"],
            "Count": [
                task_stats.get("active_tasks", 0),
                task_stats.get("scheduled_tasks", 0),
                task_stats.get("reserved_tasks", 0),
            ],
        }
        df_queue = pd.DataFrame(queue_data)
        fig = px.bar(df_queue, x="Metric", y="Count", title="Task Queue Status")
        st.plotly_chart(fig, use_container_width=True)

    # Engine Status
    st.subheader("Engine Status")
    engines_health = get_engines_health()
    if engines_health:
        engines = engines_health.get("engines", {})
        for engine_name, engine_info in engines.items():
            status = "🟢 Available" if engine_info.get("available") else "🔴 Unavailable"
            st.write(f"**{engine_name.capitalize()}**: {status}")
            if engine_info.get("info"):
                st.json(engine_info["info"])


# Submit Evaluation Page
elif page == "Submit Evaluation":
    st.header("📤 Submit Evaluation Task")

    fen = st.text_input(
        "FEN String",
        value="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        help="Enter the FEN string of the position to evaluate",
    )

    col1, col2 = st.columns(2)

    with col1:
        engine = st.selectbox("Engine", ["stockfish", "lczero"])
        depth = st.slider("Depth", min_value=1, max_value=30, value=15)

    with col2:
        time_limit = st.number_input(
            "Time Limit (seconds)", min_value=0.1, max_value=300.0, value=0.0, step=0.1
        )
        if time_limit == 0.0:
            time_limit = None

    if st.button("Submit Evaluation"):
        with st.spinner("Submitting task..."):
            result = submit_evaluation(fen, engine, depth, time_limit)
            if result:
                st.success(f"Task submitted! Task ID: {result['task_id']}")
                st.json(result)


# Task Status Page
elif page == "Task Status":
    st.header("📋 Task Status")

    task_id = st.text_input("Enter Task ID")

    if task_id:
        if st.button("Check Status") or True:
            status = get_task_status(task_id)
            if status:
                st.json(status)

                if status.get("result"):
                    result = status["result"]
                    st.subheader("Evaluation Result")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Evaluation", f"{result.get('evaluation', 0):.2f} pawns")
                    with col2:
                        st.metric(
                            "Computation Time",
                            f"{result.get('computation_time', 0):.3f}s",
                        )
                    with col3:
                        st.metric("Depth", result.get("depth", "N/A"))

                    if result.get("best_move"):
                        st.write(f"**Best Move**: {result['best_move']}")
                    if result.get("pv"):
                        st.write(f"**Principal Variation**: {' → '.join(result['pv'])}")
            else:
                st.error("Task not found or error retrieving status")


# Engine Status Page
elif page == "Engine Status":
    st.header("⚙️ Engine Status")

    engines_health = get_engines_health()
    if engines_health:
        engines = engines_health.get("engines", {})
        for engine_name, engine_info in engines.items():
            with st.expander(f"{engine_name.capitalize()} Engine", expanded=True):
                available = engine_info.get("available", False)
                st.write(f"**Status**: {'🟢 Available' if available else '🔴 Unavailable'}")

                info = engine_info.get("info", {})
                if info:
                    st.write("**Information**:")
                    st.json(info)

                if engine_info.get("error"):
                    st.error(f"Error: {engine_info['error']}")
    else:
        st.error("Unable to retrieve engine status. Check API connection.")

