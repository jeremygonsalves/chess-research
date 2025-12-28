"""Generate 3D CSS chess board HTML from chess board state."""

import chess
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
    """
    rank = 7 - (square // 8)  # Invert rank for display (0 = top rank 8)
    file = square % 8
    return (rank, file)


def generate_3d_board_html(board: chess.Board) -> str:
    """Generate HTML for 3D CSS chess board based on current board state.
    
    Args:
        board: chess.Board object
        
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
    
    # Complete HTML template
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
<DIV class="object3d chess-defaults" style="--x: 45deg; --y: 0deg; --z: 0deg; --tx: 0px; --ty: 0px; --tz: 215px; --s: 0.6; --p: 3705px;">
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

<!-- Camera Controls -->
<SPAN id="controls" class="hide">
<span class="title">Rotation</span>
<label>
<span title="Horizontal Rotation ↔">X</span>
<input type="range" id="y_axis" min="-180" max="180" value="0" onchange="apply(this, '--y', 'deg')" oninput="apply(this, '--y', 'deg')" step="0.1"/>
<span></span>
</label>

<label>
<span title="Vertical Rotation ↕">Y</span>
<input type="range" id="x_axis" min="-180" max="180" value="45" onchange="apply(this, '--x', 'deg')" oninput="apply(this, '--x', 'deg')" step="0.1"/>
<span></span>
</label>

<label>
<span title="Rotation ↔ ↕">Z</span>
<input type="range" id="z_axis" min="-180" max="180" value="-40" onchange="apply(this, '--z', 'deg')" oninput="apply(this, '--z', 'deg')" step="0.1"/>
<span></span>
</label>

<span class="title">Transform</span>
<label>
<span title="Translate X">X</span>
<input type="range" id="ty_axis" min="-2000" max="2000" value="0" onchange="apply(this, '--ty', 'px')" oninput="apply(this, '--ty', 'px')" step="1"/>
<span></span>
</label>

<label>
<span title="Translate Y">Y</span>
<input type="range" id="tz_axis" min="-2000" max="2000" value="215" onchange="apply(this, '--tz', 'px')" oninput="apply(this, '--tz', 'px')" step="1"/>
<span></span>
</label>

<label>
<span title="Translate Z">Z</span>
<input type="range" id="tx_axis" min="-2000" max="1000" value="0" onchange="apply(this, '--tx', 'px')" oninput="apply(this, '--tx', 'px')" step="1"/>
<span></span>
</label>

<label>
<span title="Scale">S</span>
<input type="range" id="scale" min="0.1" max="2" value="0.6" onchange="apply(this, '--s')" oninput="apply(this, '--s')" step="0.1"/>
<span></span>
</label>

<label>
<span title="Perspective">P</span>
<input type="range" id="perspective" min="1000" max="8000" value="3705" onchange="apply(this, '--p', 'px')" oninput="apply(this, '--p', 'px')" step="1"/>
<span></span>
</label>
<br>
<center>
<button class="board-borders" onclick="document.documentElement.classList.toggle('noborders')">Borders</button>
<button class="piece-highlighter" onclick="document.documentElement.classList.toggle('highlighted')">Highlight Pieces</button>
<br>
<button class="anim-boost" onclick="document.documentElement.classList.toggle('noanimations')">Animations</button>
<button class="body-scroll" onclick="document.documentElement.classList.toggle('noscroll')">Scroll</button>
<br>
<button class="spin360" onclick="document.documentElement.classList.toggle('rotating');document.querySelector('.object3d').classList.toggle('rotate')">Spin 360°</button>
<button class="ehide" onclick="controls.classList.toggle('hide')">Controls</button>
</center>
</SPAN>

<script>
// Click to move pieces functionality
let selectedSquare = null;
const boardSquares = {};

// Initialize square click handlers
document.addEventListener('DOMContentLoaded', function() {{
    const board = document.getElementById('chessBoard');
    const pieces = board.querySelectorAll('.piece');
    
    pieces.forEach(piece => {{
        const v = parseInt(piece.style.getPropertyValue('--v') || '0');
        const h = parseInt(piece.style.getPropertyValue('--h') || '0');
        const squareKey = `${{v}}_${{h}}`;
        
        piece.style.cursor = 'pointer';
        piece.addEventListener('click', function(e) {{
            e.stopPropagation();
            handleSquareClick(squareKey, piece);
        }});
        
        boardSquares[squareKey] = {{
            piece: piece,
            rank: v,
            file: h
        }};
    }});
    
    // Add click handlers to empty squares (we'll create invisible divs)
    for (let rank = 0; rank < 8; rank++) {{
        for (let file = 0; file < 8; file++) {{
            const squareKey = `${{rank}}_${{file}}`;
            if (!boardSquares[squareKey]) {{
                const emptySquare = document.createElement('div');
                emptySquare.className = 'empty-square';
                emptySquare.style.cssText = `
                    position: absolute;
                    left: calc(100px * ${{file}});
                    bottom: calc(100px * ${{rank}});
                    width: 100px;
                    height: 100px;
                    cursor: pointer;
                    z-index: 1;
                `;
                emptySquare.addEventListener('click', function() {{
                    handleSquareClick(squareKey, null);
                }});
                board.appendChild(emptySquare);
                boardSquares[squareKey] = {{
                    piece: null,
                    rank: rank,
                    file: file
                }};
            }}
        }}
    }}
}});

function handleSquareClick(squareKey, pieceElement) {{
    const rank = parseInt(squareKey.split('_')[0]);
    const file = parseInt(squareKey.split('_')[1]);
    
    // Convert to chess notation (rank 0-7 to 8-1, file 0-7 to a-h)
    const chessRank = 8 - rank;
    const chessFile = String.fromCharCode(97 + file); // a-h
    const fromSquare = chessFile + chessRank;
    
    if (selectedSquare === null) {{
        // First click - select piece
        if (pieceElement) {{
            selectedSquare = squareKey;
            pieceElement.style.boxShadow = '0 0 20px rgba(0, 200, 0, 0.8)';
            pieceElement.style.transform += ' scale(1.1)';
        }}
    }} else {{
        // Second click - move
        const selectedData = boardSquares[selectedSquare];
        const selectedRank = 8 - selectedData.rank;
        const selectedFile = String.fromCharCode(97 + selectedData.file);
        const toSquare = chessFile + chessRank;
        const moveUCI = selectedFile + selectedRank + toSquare;
        
        // Clear previous selection
        const prevPiece = boardSquares[selectedSquare].piece;
        if (prevPiece) {{
            prevPiece.style.boxShadow = '';
            prevPiece.style.transform = prevPiece.style.transform.replace(' scale(1.1)', '');
        }}
        
        // Store move in URL hash or trigger Streamlit update
        // Since Streamlit iframes can't easily communicate back,
        // we'll use a simpler approach: display the move and let user confirm
        const moveDisplay = document.getElementById('moveDisplay');
        if (moveDisplay) {{
            moveDisplay.innerHTML = `
                <div style="position:fixed;top:10px;right:10px;background:rgba(0,200,0,0.9);padding:15px;border-radius:5px;z-index:10000;color:white;font-weight:bold;">
                    Move: ${{moveUCI}}<br>
                    <button onclick="window.location.reload()" style="margin-top:10px;padding:5px 10px;cursor:pointer;">Confirm</button>
                </div>
            `;
        }}
        
        // Also try to communicate with Streamlit parent
        try {{
            if (window.parent && window.parent.postMessage) {{
                window.parent.postMessage({{
                    type: 'chess_move',
                    move: moveUCI
                }}, '*');
            }}
        }} catch(e) {{
            console.log('Could not send message to parent:', e);
        }}
        
        // Store in localStorage as backup
        localStorage.setItem('pending_move', moveUCI);
        
        selectedSquare = null;
    }}
}}

// Camera control function (kept for manual controls if needed)
function apply(i,o,u){{
var output;
if(u){{output = i.value + (u + '')}}
else{{output = Number(i.value)}}
document.documentElement.style.setProperty(o, output);
if(i.nextElementSibling) i.nextElementSibling.innerHTML = output;
}}

// Set default camera position (no auto-rotation)
window.addEventListener('load', function(){{
setTimeout(function(){{
const object3d = document.querySelector('.object3d');
if(object3d) {{
    object3d.style.setProperty('--x', '45deg');
    object3d.style.setProperty('--y', '0deg');
    object3d.style.setProperty('--z', '0deg');
    object3d.style.setProperty('--tx', '0px');
    object3d.style.setProperty('--ty', '0px');
    object3d.style.setProperty('--tz', '215px');
    object3d.style.setProperty('--s', '0.6');
    object3d.style.setProperty('--p', '3705px');
}}

if (typeof x_axis !== 'undefined') {{
    apply(x_axis, '--x', 'deg');
    apply(y_axis, '--y', 'deg');
    apply(z_axis, '--z', 'deg');
    apply(tx_axis, '--tx', 'px');
    apply(ty_axis, '--ty', 'px');
    apply(tz_axis, '--tz', 'px');
    apply(perspective, '--p', 'px');
    apply(scale, '--s');
}}

setTimeout(function(){{
document.documentElement.classList.add("scalable");
}}, 100);
}}, 100);
}});
</script>
<div id="moveDisplay"></div>
<script>
// Check for pending move from previous interaction
const pendingMove = localStorage.getItem('pending_move');
if (pendingMove) {{
    localStorage.removeItem('pending_move');
    const moveDisplay = document.getElementById('moveDisplay');
    if (moveDisplay) {{
        moveDisplay.innerHTML = `
            <div style="position:fixed;top:10px;right:10px;background:rgba(0,200,0,0.9);padding:15px;border-radius:5px;z-index:10000;color:white;font-weight:bold;">
                Pending Move: ${{pendingMove}}
            </div>
        `;
    }}
}}
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


def get_chess_board_css() -> str:
    """Return the complete CSS for the 3D chess board."""
    from pathlib import Path
    
    css_file = Path(__file__).parent / "chess_board_3d.css"
    if css_file.exists():
        return css_file.read_text()
    else:
        # Fallback minimal CSS if file not found
        return "/* CSS file not found */"

