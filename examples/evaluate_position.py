"""Example script for evaluating chess positions."""

import requests
import time
import sys

API_BASE_URL = "http://localhost:8000/api/v1"


def evaluate_position(fen: str, engine: str = "stockfish", depth: int = 15):
    """Submit and wait for evaluation result."""
    
    # Submit evaluation
    print(f"Submitting evaluation for position...")
    print(f"FEN: {fen}")
    print(f"Engine: {engine}, Depth: {depth}")
    
    response = requests.post(
        f"{API_BASE_URL}/evaluate",
        json={
            "fen": fen,
            "engine": engine,
            "depth": depth,
        }
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
    task_status = response.json()
    task_id = task_status["task_id"]
    print(f"Task ID: {task_id}")
    print("Waiting for evaluation...")
    
    # Poll for result
    while True:
        status_response = requests.get(f"{API_BASE_URL}/evaluate/{task_id}")
        if status_response.status_code != 200:
            print(f"Error checking status: {status_response.text}")
            break
            
        status = status_response.json()
        
        if status["status"] == "completed":
            result = status["result"]
            print("\n✅ Evaluation Complete!")
            print(f"Evaluation: {result['evaluation']:.2f} pawns")
            print(f"Best Move: {result.get('best_move', 'N/A')}")
            print(f"Computation Time: {result['computation_time']:.3f}s")
            if result.get("pv"):
                print(f"Principal Variation: {' → '.join(result['pv'][:5])}")
            return result
        elif status["status"] == "failed":
            print(f"\n❌ Evaluation Failed: {status.get('result', {}).get('error', 'Unknown error')}")
            return None
        
        time.sleep(0.5)
        print(".", end="", flush=True)


if __name__ == "__main__":
    # Example: Starting position
    starting_position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    # Example: A more interesting position (Ruy Lopez opening)
    ruy_lopez = "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
    
    # Use provided FEN or default
    fen = sys.argv[1] if len(sys.argv) > 1 else starting_position
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    
    evaluate_position(fen, depth=depth)

