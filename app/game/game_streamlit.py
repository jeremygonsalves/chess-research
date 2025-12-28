"""Streamlit interface for interactive chess game."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import chess
from app.game.chess_game import ChessGame


# Must be first Streamlit command
st.set_page_config(
    page_title="Interactive Chess Game",
    page_icon="♟️",
    layout="wide",
)

st.title("♟️ Interactive Chess Game with Optimal Moves")
st.markdown("Play chess and get optimal move recommendations at each step. Perfect for collecting training data!")

# Initialize game in session state
if 'game' not in st.session_state:
    try:
        st.session_state.game = ChessGame(depth=15)
        st.session_state.move_history = []
    except Exception as e:
        st.error(f"Error initializing Stockfish: {e}")
        st.stop()

game = st.session_state.game

# Sidebar controls
st.sidebar.header("Game Controls")

if st.sidebar.button("Reset Game"):
    game.reset()
    st.session_state.move_history = []
    st.rerun()

if st.sidebar.button("Export Training Data"):
    filename = f"chess_training_data_{game.move_count}moves.json"
    game.export_training_data(filename)
    st.sidebar.success(f"Saved to {filename}")

st.sidebar.markdown("---")
st.sidebar.write(f"**Moves:** {game.move_count}")
st.sidebar.write(f"**Turn:** {'White' if game.board.turn else 'Black'}")

if game.board.is_game_over():
    st.sidebar.warning(f"Game Over: {game.board.result()}")
    
    # Show accuracy analysis
    with st.sidebar.expander("📊 Game Accuracy Analysis", expanded=True):
        accuracy_data = game.analyze_game_accuracy()
        
        if accuracy_data["total_positions"] > 0:
            st.metric(
                "Accuracy", 
                accuracy_data["accuracy_percentage"],
                help="Percentage of moves that matched Stockfish's optimal recommendation"
            )
            st.write(f"**Optimal moves:** {accuracy_data['optimal_moves']}")
            st.write(f"**Suboptimal moves:** {accuracy_data['suboptimal_moves']}")
            st.write(f"**Total positions:** {accuracy_data['total_positions']}")
            
            # Show move-by-move breakdown
            if st.checkbox("Show move details", key="show_accuracy_details"):
                st.write("**Move-by-move analysis:**")
                for detail in accuracy_data["move_details"]:
                    status = "✅" if detail["is_optimal"] else "❌"
                    eval_str = f" (Eval: {detail.get('evaluation_before', 'N/A'):.2f})" if detail.get('evaluation_before') else ""
                    st.write(f"{status} Move {detail['move_number']}: Played `{detail['move_played']}`, Optimal: `{detail['optimal_move']}`{eval_str}")
        else:
            if game.move_count == 0:
                st.info("Play some moves to see accuracy analysis")
            else:
                st.warning(f"No accuracy data available. Total moves: {game.move_count}, History entries: {len(game.game_history)}")
                if st.button("Debug - Show game history", key="debug_history"):
                    st.json(game.game_history)

# Main content - split into columns
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Chess Board")
    st.info("💡 **Click a piece, then click its destination square to make a move**")
    
    # Display 3D chess board
    from app.game.chess_board_interactive import generate_3d_board_html
    import streamlit.components.v1 as components
    
    # Generate board with current move count and legal moves for highlighting
    legal_moves = game.get_legal_moves()
    board_html = generate_3d_board_html(game.board, move_count=game.move_count, legal_moves=legal_moves)
    
    # Create a container div with ID for JavaScript to update
    st.markdown('<div id="move-display-area"></div>', unsafe_allow_html=True)
    
    # Display board with message listener
    # Note: components.html doesn't support 'key', so we embed move_count in HTML for uniqueness
    components.html(
        board_html, 
        height=700, 
        scrolling=False
    )
    
    # Add JavaScript to listen for moves from iframe and update Streamlit
    st.markdown("""
    <script>
    (function() {{
        // Poll for moves in localStorage (works across iframe boundary)
        let lastChecked = 0;
        const checkInterval = setInterval(function() {{
            try {{
                const moveTimestamp = localStorage.getItem('move_timestamp');
                if (moveTimestamp && parseInt(moveTimestamp) > lastChecked) {{
                    const move = localStorage.getItem('chess_move');
                    if (move) {{
                        lastChecked = parseInt(moveTimestamp);
                        
                        // Find the move input field by placeholder or label
                        const inputs = Array.from(document.querySelectorAll('input[type="text"]'));
                        const moveInput = inputs.find(input => 
                            (input.placeholder && input.placeholder.includes('UCI')) ||
                            (input.placeholder && input.placeholder.includes('click pieces'))
                        );
                        
                        if (moveInput && moveInput.value !== move) {{
                            // Set value and trigger change events
                            moveInput.value = move;
                            moveInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            moveInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            moveInput.focus();
                            
                            // Also try setting it via value property
                            Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(moveInput, move);
                            moveInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }}
                        
                        // Show notification
                        const area = document.getElementById('move-display-area');
                        if (area) {{
                            area.innerHTML = '<div style="padding:15px;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius:8px;margin:10px 0;color:white;font-weight:bold;box-shadow:0 4px 15px rgba(0,0,0,0.2);">✅ Move selected: <strong style="font-size:1.2em;">' + move + '</strong><br><small>Click "Play Move" button to confirm</small></div>';
                        }}
                    }}
                }}
            }} catch(e) {{
                // Cross-origin or other error, ignore silently
                console.log('Move check error (safe to ignore):', e);
            }}
        }}, 300);
        
        // Listen for postMessage from iframe
        window.addEventListener('message', function(event) {{
            if (event.data && event.data.type === 'chess_move') {{
                const move = event.data.move;
                const inputs = Array.from(document.querySelectorAll('input[type="text"]'));
                const moveInput = inputs.find(input => 
                    input.placeholder && (input.placeholder.includes('UCI') || input.placeholder.includes('click pieces'))
                );
                if (moveInput) {{
                    moveInput.value = move;
                    moveInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    moveInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            }}
        }});
    }})();
    </script>
    """, unsafe_allow_html=True)
    
    # Show FEN for reference
    with st.expander("Position Details"):
        st.text(f"FEN: {game.board.fen()}")
        st.text(f"Move: {game.move_count}")
        st.text(f"Turn: {'White' if game.board.turn else 'Black'}")
    
    # Get optimal move
    if not game.board.is_game_over():
        with st.spinner("Calculating optimal move..."):
            analysis = game.get_position_analysis()
        
        if analysis.get("best_move"):
            st.success(f"🎯 **Optimal Move:** {analysis['best_move']}")
            st.info(f"📊 **Evaluation:** {analysis['evaluation']:.2f} pawns ({'White' if analysis['evaluation'] > 0 else 'Black'} advantage)")
            
            if analysis.get("pv"):
                st.write("**Principal Variation:**")
                pv_display = " → ".join(analysis['pv'][:8])
                st.code(pv_display)

with col2:
    st.header("Make a Move")
    
    # Get legal moves
    legal_moves = game.get_legal_moves()
    
    # Move input - auto-populate from board clicks
    # Check for move from localStorage (set by board clicks)
    if 'last_move_check' not in st.session_state:
        st.session_state.last_move_check = 0
    
    # Move input field
    move_input = st.text_input(
        "Enter move (UCI format) - or click pieces on board 👆", 
        value="",
        placeholder="e2e4 (or click pieces above)", 
        key="move_input"
    )
    
    # Display helper text if no move entered
    if not move_input:
        st.caption("💡 **Tip:** Click a piece, then click its destination square. The move will appear here automatically!")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Play Move", type="primary"):
            if move_input:
                success, message = game.make_move(move_input)
                if success:
                    st.success(message)
                    st.session_state.move_history.append(move_input)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please enter a move")
    
    with col_btn2:
        if st.button("Play Optimal Move"):
            if not game.board.is_game_over():
                analysis = game.get_position_analysis()
                if analysis.get("best_move"):
                    success, message = game.make_move(analysis['best_move'])
                    if success:
                        st.success(f"Played: {analysis['best_move']}")
                        st.session_state.move_history.append(analysis['best_move'])
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.warning("Game is over!")
    
    st.markdown("---")
    st.write("**Quick Move Buttons:**")
    
    # Show some common opening moves if at start
    if game.move_count == 0:
        common_moves = ["e2e4", "d2d4", "g1f3", "c2c4"]
        for move in common_moves:
            if move in legal_moves:
                if st.button(f"Play {move}", key=f"quick_{move}"):
                    success, message = game.make_move(move)
                    if success:
                        st.session_state.move_history.append(move)
                        st.rerun()

    st.markdown("---")
    st.write("**Legal Moves:**")
    # Display legal moves in columns
    cols = st.columns(5)
    for i, move in enumerate(legal_moves[:20]):  # Show first 20
        with cols[i % 5]:
            if st.button(move, key=f"legal_{move}"):
                success, message = game.make_move(move)
                if success:
                    st.session_state.move_history.append(move)
                    st.rerun()

# Move history
st.header("Move History")
if st.session_state.move_history:
    moves_display = " ".join([f"{i+1}. {move}" if i % 2 == 0 else f"{move} " 
                              for i, move in enumerate(st.session_state.move_history)])
    st.text(moves_display)
else:
    st.write("No moves yet")

# Training data info
st.sidebar.markdown("---")
st.sidebar.header("Training Data")
st.sidebar.write(f"**Positions collected:** {len(game.game_history)}")
st.sidebar.write(f"**Total moves:** {game.move_count}")

