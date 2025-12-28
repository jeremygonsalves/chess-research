#!/bin/bash
# Run Streamlit chess game from project root

cd "$(dirname "$0")"
streamlit run app/game/game_streamlit.py --server.port=8502

