#!/usr/bin/env python3

import sys
import time
import chess
from stockfish_engine import StockfishEngine

def uci_loop():
    """
    The main loop to handle UCI commands.
    """
    board = chess.Board()
    engine = StockfishEngine()

    while True:
        line = sys.stdin.readline().strip()
        if line == "quit":
            break
        elif line == "uci":
            print("id name sejal")
            print("id author ishworkhanal")
            print("uciok")
        elif line == "isready":
            print("readyok")
        elif line == "ucinewgame":
            board.reset()
        elif line.startswith("position"):
            parts = line.split(" ")
            if parts[1] == "startpos":
                board.reset()
                moves_start_index = 2
            elif parts[1] == "fen":
                fen = " ".join(parts[2:8])
                board.set_fen(fen)
                moves_start_index = 8
            else:
                continue
            if len(parts) > moves_start_index and parts[moves_start_index] == "moves":
                for move_uci in parts[moves_start_index + 1:]:
                    board.push_uci(move_uci)
        elif line.startswith("go"):
            search_depth = 20
            engine.set_depth(search_depth)
            start_time = time.perf_counter()
            
            best_move_uci = engine.get_best_move(board.fen())
            score = engine.get_evaluation(board.fen())
            
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time

            if abs(score) >= 999:
                mate_in = 1 if score > 0 else -1
                score_string = f"mate {mate_in}"
            else:
                score_string = f"cp {int(score * 100)}"

            print(f"info depth {search_depth} score {score_string} time {int(elapsed_time * 1000)}")
            if best_move_uci:
                print(f"bestmove {best_move_uci}")
            else:
                legal_moves = list(board.legal_moves)
                if legal_moves:
                    print(f"bestmove {legal_moves[0].uci()}")
                else:
                    print("bestmove 0000")
        sys.stdout.flush()


if __name__ == "__main__":
    uci_loop()
