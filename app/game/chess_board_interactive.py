"""Generate interactive 3D chess board HTML from chess board state with drag and drop."""

import chess
import json
from typing import Dict


def get_piece_class(piece: chess.Piece) -> str:
    """Convert chess.Piece to CSS class name."""
    piece_map = {
        chess.PAWN: "PAWN",
        chess.ROOK: "ROOK",
        chess.KNIGHT: "HORSE",
        chess.BISHOP: "BISHOP",
        chess.QUEEN: "QUEEN",
        chess.KING: "KING",
    }
    return piece_map.get(piece.piece_type, "")


def get_square_position(square: int) -> tuple:
    """Convert square index to (rank, file) position.
    
    Args:
        square: Square index (0-63)
        
    Returns:
        Tuple of (rank, file) where rank is 0-7 (0=rank 8, 7=rank 1)
        and file is 0-7 (0=a-file, 7=h-file)
        
    Note: For white at bottom, we flip the rank so white pieces (rank 1-2) appear at bottom
    """
    rank = square // 8  # Original: 7 - (square // 8) was inverting
    file = square % 8
    return (rank, file)


def get_chess_board_css() -> str:
    """Return the complete CSS for the 3D chess board."""
    from pathlib import Path
    
    css_file = Path(__file__).parent / "chess_board_3d.css"
    if css_file.exists():
        css_content = css_file.read_text()
        # Add minimal drag and drop styles
        css_content += """
.piece {
    cursor: grab;
}

.piece:active {
    cursor: grabbing;
}

.piece.dragging {
    opacity: 0.7;
    z-index: 1000;
}

.empty-square {
    position: absolute;
    cursor: pointer;
    z-index: 5;
}

.empty-square.drag-over {
    background: rgba(0, 255, 0, 0.5) !important;
    border: 3px solid rgba(0, 255, 0, 0.8) !important;
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.6) !important;
}

.empty-square.valid-move {
    background: rgba(0, 150, 255, 0.4) !important;
    border: 2px solid rgba(0, 150, 255, 0.7) !important;
    box-shadow: 0 0 15px rgba(0, 150, 255, 0.5) !important;
    border-radius: 50%;
}

.piece.valid-move {
    background: rgba(0, 150, 255, 0.4) !important;
    border: 2px solid rgba(0, 150, 255, 0.7) !important;
    box-shadow: 0 0 15px rgba(0, 150, 255, 0.5) !important;
    border-radius: 50%;
}
"""
        return css_content
    else:
        return "/* CSS file not found */"


def generate_3d_board_html(board: chess.Board, move_count: int = 0, legal_moves: list = None) -> str:
    """Generate HTML for 3D CSS chess board based on current board state with drag and drop.
    
    Args:
        board: chess.Board object
        move_count: Current move count (for refresh tracking)
        
    Returns:
        Complete HTML string with 3D board
    """
    # Generate piece HTML
    pieces_html = []
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            rank, file = get_square_position(square)
            piece_class = get_piece_class(piece)
            color_class = "BLACK " if piece.color == chess.BLACK else ""
            
            # Generate piece HTML based on type
            piece_html = generate_piece_html(piece_class, color_class, rank, file)
            pieces_html.append(piece_html)
    
    pieces_html_str = "\n\t\t".join(pieces_html)
    
    # Get legal moves if not provided
    if legal_moves is None:
        legal_moves = [str(move) for move in board.legal_moves]
    
    # Create legal moves map: from_square -> [to_squares]
    legal_moves_map = {}
    for move_uci in legal_moves:
        if len(move_uci) >= 4:
            from_sq = move_uci[:2]
            to_sq = move_uci[2:4]
            if from_sq not in legal_moves_map:
                legal_moves_map[from_sq] = []
            legal_moves_map[from_sq].append(to_sq)
    
    # Convert to JSON string for JavaScript
    legal_moves_json = json.dumps(legal_moves_map)
    
    # Complete HTML template - ORIGINAL structure, camera adjusted for overhead view
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3D Chess Board</title>
<style>
{get_chess_board_css()}
</style>
</head>
<body>
<DIV class="uniform">
<DIV class="object3d chess-defaults" style="--x: 30deg; --y: 4deg; --z: 0deg; --tx: -100px; --ty: -150px; --tz: -500px; --s: 0.6; --p: 3705px;">
<!-- The Stage -->
<div class="reusable-rect main-stage">
	<div class="sides side1"></div>
	<div class="sides side2"></div>

	<!-- Elements over Stage -->
	<div class="main-elements">
		<DIV class="board" id="chessBoard">
		{pieces_html_str}
		</DIV>
		<DIV class="coordinates"></DIV>
		<DIV class="coordinates_"></DIV>
	</div>
</div>
</DIV>
</DIV>

<div id="moveNotification" style="position:fixed;top:20px;right:20px;background:rgba(0,200,0,0.9);padding:20px;border-radius:10px;z-index:10000;color:white;font-weight:bold;font-size:18px;display:none;box-shadow:0 4px 20px rgba(0,0,0,0.3);">
	<div id="moveText"></div>
	<button onclick="confirmMove()" style="margin-top:10px;padding:10px 20px;cursor:pointer;background:white;border:none;border-radius:5px;font-weight:bold;">Confirm Move</button>
	<button onclick="cancelMove()" style="margin-top:10px;margin-left:10px;padding:10px 20px;cursor:pointer;background:#ccc;border:none;border-radius:5px;">Cancel</button>
</div>

<script>
// Legal moves map: from_square -> [to_squares]
const legalMovesMap = {legal_moves_json};

// Drag and drop state
let draggedPiece = null;
let draggedSquare = null;
let validMoveSquares = [];

// Initialize drag and drop
document.addEventListener('DOMContentLoaded', function() {{
    const board = document.getElementById('chessBoard');
    const pieces = board.querySelectorAll('.piece');
    
    // Setup pieces for drag and drop
    pieces.forEach(piece => {{
        const v = parseInt(piece.style.getPropertyValue('--v') || '0');
        const h = parseInt(piece.style.getPropertyValue('--h') || '0');
        
        // Convert to UCI notation
        const chessRank = 8 - v;
        const chessFile = String.fromCharCode(97 + h);
        const squareUCI = chessFile + chessRank;
        
        piece.setAttribute('draggable', 'true');
        piece.setAttribute('data-square', squareUCI);
        
        piece.addEventListener('dragstart', function(e) {{
            draggedPiece = this;
            draggedSquare = squareUCI;
            this.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', squareUCI);
            
            // Highlight valid destination squares (both empty and occupied)
            validMoveSquares = legalMovesMap[squareUCI] || [];
            validMoveSquares.forEach(toSquare => {{
                // Check both empty squares and pieces
                const targetSquare = document.querySelector(`[data-square="${{toSquare}}"]`);
                const targetPiece = document.querySelector(`.piece[data-square="${{toSquare}}"]`);
                if (targetSquare) {{
                    targetSquare.classList.add('valid-move');
                }}
                if (targetPiece) {{
                    targetPiece.classList.add('valid-move');
                }}
            }});
        }});
        
        piece.addEventListener('dragend', function(e) {{
            this.classList.remove('dragging');
            document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
            document.querySelectorAll('.valid-move').forEach(el => el.classList.remove('valid-move'));
            draggedPiece = null;
            draggedSquare = null;
            validMoveSquares = [];
        }});
        
        // Also handle drop on pieces (for captures)
        piece.addEventListener('dragover', function(e) {{
            if (draggedSquare && draggedSquare !== squareUCI && validMoveSquares.includes(squareUCI)) {{
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                this.classList.add('drag-over');
            }}
        }});
        
        piece.addEventListener('dragleave', function(e) {{
            this.classList.remove('drag-over');
        }});
        
        piece.addEventListener('drop', function(e) {{
            e.preventDefault();
            this.classList.remove('drag-over');
            this.classList.remove('valid-move');
            
            if (draggedSquare && validMoveSquares.includes(squareUCI)) {{
                const move = draggedSquare + squareUCI;
                completeMove(move);
            }}
        }});
    }});
    
    // Create empty squares for drop targets
    for (let rank = 0; rank < 8; rank++) {{
        for (let file = 0; file < 8; file++) {{
            const squareKey = `${{rank}}_${{file}}`;
            const existingPiece = Array.from(pieces).find(p => {{
                const pv = parseInt(p.style.getPropertyValue('--v') || '0');
                const ph = parseInt(p.style.getPropertyValue('--h') || '0');
                return pv === rank && ph === file;
            }});
            
            if (!existingPiece) {{
                const chessRank = 8 - rank;
                const chessFile = String.fromCharCode(97 + file);
                const squareUCI = chessFile + chessRank;
                
                const emptySquare = document.createElement('div');
                emptySquare.className = 'empty-square';
                emptySquare.setAttribute('data-square', squareUCI);
                emptySquare.style.cssText = `
                    position: absolute;
                    left: calc(100px * ${{file}});
                    bottom: calc(100px * ${{rank}});
                    width: 100px;
                    height: 100px;
                    background: transparent;
                `;
                
                emptySquare.addEventListener('dragover', function(e) {{
                    e.preventDefault();
                    // Only allow drop if this is a valid move
                    if (draggedSquare && validMoveSquares.includes(squareUCI)) {{
                        e.dataTransfer.dropEffect = 'move';
                        this.classList.add('drag-over');
                    }} else {{
                        e.dataTransfer.dropEffect = 'none';
                    }}
                }});
                
                emptySquare.addEventListener('dragleave', function(e) {{
                    this.classList.remove('drag-over');
                }});
                
                emptySquare.addEventListener('drop', function(e) {{
                    e.preventDefault();
                    this.classList.remove('drag-over');
                    this.classList.remove('valid-move');
                    
                    if (draggedSquare && validMoveSquares.includes(squareUCI)) {{
                        const move = draggedSquare + squareUCI;
                        completeMove(move);
                    }}
                }});
                
                board.appendChild(emptySquare);
            }}
        }}
    }}
}});

function completeMove(move) {{
    window.pendingMove = move;
    
    const notification = document.getElementById('moveNotification');
    if (notification) {{
        document.getElementById('moveText').textContent = 'Move: ' + move;
        notification.style.display = 'block';
    }}
    
    localStorage.setItem('chess_move', move);
    localStorage.setItem('move_timestamp', Date.now().toString());
    
    try {{
        if (window.parent && window.parent !== window) {{
            window.parent.postMessage({{
                type: 'chess_move',
                move: move
            }}, '*');
        }}
    }} catch(e) {{
        console.log('Could not send message:', e);
    }}
}}

function confirmMove() {{
    if (window.pendingMove) {{
        const move = window.pendingMove;
        localStorage.setItem('chess_move', move);
        localStorage.setItem('move_timestamp', Date.now().toString());
        document.getElementById('moveNotification').style.display = 'none';
        window.pendingMove = null;
        setTimeout(() => {{ window.location.reload(); }}, 300);
    }}
}}

function cancelMove() {{
    window.pendingMove = null;
    document.getElementById('moveNotification').style.display = 'none';
}}

// Camera control function
function apply(i,o,u){{
var output;
if(u){{output = i.value + (u + '')}}
else{{output = Number(i.value)}}
document.documentElement.style.setProperty(o, output);
if(i.nextElementSibling) i.nextElementSibling.innerHTML = output;
}}

// Set fixed camera position - 180deg Y rotation (white at bottom), prevent auto-rotation
window.addEventListener('load', function(){{
setTimeout(function(){{
const object3d = document.querySelector('.object3d');
if(object3d) {{
    // Prevent auto-rotation
    object3d.classList.remove('rotate');
    document.documentElement.classList.remove('rotating');
    
    // Set camera - overhead view with steeper angle (white at bottom via piece positioning)
    object3d.style.setProperty('--x', '30deg');  // Steeper angle from top
    object3d.style.setProperty('--y', '4deg');
    object3d.style.setProperty('--z', '0deg');
    object3d.style.setProperty('--tx', '-90px');  // Moved left from user's perspective (more negative = left)
    object3d.style.setProperty('--ty', '-700px');  // Moved down further (negative = down to show white pieces)
    object3d.style.setProperty('--tz', '-900px');  // Zoomed out even more (negative value = very far away)
    object3d.style.setProperty('--s', '0.6');
    object3d.style.setProperty('--p', '3705px');
    object3d.style.animation = 'none';
}}

// Don't apply controls (they don't exist in our version)
// Just add scalable class
setTimeout(function(){{
document.documentElement.classList.add("scalable");
}}, 1000);
}}, 1000);
}});
</script>
</body>
</html>"""
    
    return html


def generate_piece_html(piece_type: str, color_class: str, rank: int, file: int) -> str:
    """Generate HTML for a single chess piece.
    
    Args:
        piece_type: Piece type (PAWN, ROOK, etc.)
        color_class: "BLACK " or ""
        rank: Rank (0-7, where 0 is rank 8)
        file: File (0-7, where 0 is a-file)
        
    Returns:
        HTML string for the piece
    """
    base_html = {
        "PAWN": """<div class="piece {color}{type}" style="--v:{rank};--h:{file};">
		<div class="reusable-rect piece-base"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
		<div class="reusable-rect piece-upbase"> <div class="sides side1"></div><div class="sides side2"></div> </div>
		<div class="reusable-rect piece-thick"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
		<div class="reusable-rect piece-head"> <div class="sides side1"></div><div class="sides side2"></div> </div>
	</div>""",
        
        "ROOK": """<div class="piece {color}{type}" style="--v:{rank};--h:{file};">
		<div class="reusable-rect piece-base"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
		<div class="reusable-rect piece-upbase"> <div class="sides side1"></div><div class="sides side2"></div> </div>
		<div class="reusable-rect piece-thick"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
		<div class="reusable-rect piece-head">
			<div class="sides side1"></div>
			<div class="sides side2"></div>
			<div class="reusable-rect piece-head-left"> <div class="sides side1"></div><div class="sides side2"></div> </div>
			<div class="reusable-rect piece-head-right"> <div class="sides side1"></div><div class="sides side2"></div> </div>
		</div>
		<div class="reusable-rect piece-head-center"> <div class="sides side1"></div><div class="sides side2"></div> </div>
	</div>""",
        
        "HORSE": """<div class="piece {color}{type}" style="--v:{rank};--h:{file};">
		<div class="reusable-rect piece-base"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
		<div class="reusable-rect piece-upbase"> <div class="sides side1"></div><div class="sides side2"></div> </div>
		<div class="reusable-rect piece-tilt1"> <div class="sides side1"></div><div class="sides side2"></div> </div>
		<div class="reusable-rect piece-tilt2"> <div class="sides side1"></div><div class="sides side2"></div> </div>
		<div class="reusable-rect piece-tilt3"> <div class="sides side1"></div><div class="sides side2"></div> </div>
	</div>""",
        
        "BISHOP": """<div class="piece {color}{type}" style="--v:{rank};--h:{file};">
		<div class="reusable-rect piece-base"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
		<div class="reusable-rect piece-upbase"> <div class="sides side1"></div><div class="sides side2"></div> </div>
		<div class="reusable-rect piece-thick"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
		<div class="reusable-rect piece-head"> <div class="sides side1"></div><div class="sides side2"></div> </div>
		<div class="piece-crown">
			<div class="ccside ccside1"></div>
			<div class="ccside ccside2"></div>
			<div class="ccside ccside3"></div>
			<div class="ccside ccside4"></div>
		</div>
	</div>""",
        
        "QUEEN": """<div class="piece {color}{type}" style="--v:{rank};--h:{file};">
		<div class="reusable-rect piece-base"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
		<div class="reusable-rect piece-upbase"> <div class="sides side1"></div><div class="sides side2"></div> </div>
		<div class="reusable-rect piece-thick"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
		<div class="piece-head">
		<div class="reusable-trapezoid">
			<div class="trapesides trapeside1"></div>
			<div class="trapesides trapeside2"></div>
			<div class="trapesides trapeside3"></div>
			<div class="trapesides trapeside4"></div>
			<div class="trapesides trapeside5"></div>
		</div>
		</div>
		<div class="reusable-rect piece-diamond"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
		<div class="reusable-rect piece-hood"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
	</div>""",
        
        "KING": """<div class="piece {color}{type}" style="--v:{rank};--h:{file};">
		<div class="reusable-rect piece-base"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
		<div class="reusable-rect piece-upbase"> <div class="sides side1"></div><div class="sides side2"></div> </div>
		<div class="reusable-rect piece-thick"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
		<div class="piece-head">
		<div class="reusable-trapezoid">
			<div class="trapesides trapeside1"></div>
			<div class="trapesides trapeside2"></div>
			<div class="trapesides trapeside3"></div>
			<div class="trapesides trapeside4"></div>
			<div class="trapesides trapeside5"></div>
		</div>
		</div>
		<div class="reusable-rect piece-diamond"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
		<div class="reusable-rect piece-hood"> <div class="sides side1"></div> <div class="sides side2"></div> </div>
	</div>""",
    }
    
    template = base_html.get(piece_type, base_html["PAWN"])
    return template.format(color=color_class, type=piece_type, rank=rank, file=file)
