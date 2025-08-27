import os
from stockfish import Stockfish

def _find_stockfish_binary(user_path=None):
    """
    Resolve a Stockfish binary path.
    Order: explicit arg -> env var -> common paths -> rely on PATH.
    """
    candidates = [
        user_path,
        os.environ.get("STOCKFISH_BINARY"),
        "/opt/homebrew/bin/stockfish",  # macOS Apple Silicon (Homebrew)
        "/usr/local/bin/stockfish",     # macOS Intel / many Linux
        "/usr/bin/stockfish",           # Linux
        "stockfish",                    # last resort: PATH
    ]
    for p in candidates:
        if p and os.path.exists(p) and os.access(p, os.X_OK):
            return p
    return None


class StockfishEngine:
    """
    Thin wrapper around PyPI 'stockfish' (3.28.0) using only documented API:
      - Stockfish(path=..., depth=..., parameters={...})
      - set_fen_position, get_best_move/get_best_move_time
      - set_depth, set_skill_level, set_elo_rating
      - update_engine_parameters
    """
    def __init__(self, depth=20, elo=None, path=None, parameters=None):
        # Defaults from the docs with safe tweaks.
        default_params = {
            "Threads": 2,                  # speed/strength
            "Hash": 64,                    # MB; increase if you want
            "Skill Level": 20,             # full strength unless Elo limited
            "MultiPV": 1,
            "Move Overhead": 10,
            "Minimum Thinking Time": 20,
            "Slow Mover": 100,
            "UCI_Chess960": "false",
            "UCI_LimitStrength": "false",
            "UCI_Elo": 1350,
            "Ponder": "false",
            "Debug Log File": "",
            "Contempt": 0,
            "Min Split Depth": 0,
        }
        if isinstance(parameters, dict):
            default_params.update(parameters)

        self.depth = int(depth)
        # If elo is set, we’ll run in Elo-limited mode; otherwise depth mode.
        self._elo_mode = elo is not None
        self.elo = int(elo) if elo is not None else None

        self.engine = None
        binary = _find_stockfish_binary(path)

        try:
            if not binary:
                raise RuntimeError("No Stockfish binary found. Set STOCKFISH_BINARY or pass path=...")

            # IMPORTANT: pass 'parameters' only when it's a dict
            self.engine = Stockfish(path=binary, depth=self.depth, parameters=default_params)

            # Apply mode
            if self._elo_mode:
                self.set_elo(self.elo)
            else:
                self.set_depth(self.depth)

        except Exception as e:
            print(f"Error initializing Stockfish: {e}")
            print("Ensure the Stockfish binary is installed and reachable. "
                  "Set STOCKFISH_BINARY=/full/path/to/stockfish if needed.")
            self.engine = None

    # ------------- Public GUI API -------------

    def is_available(self):
        return self.engine is not None

    def set_depth(self, depth: int):
        """Depth-limited (strong), disables Elo limiting."""
        self.depth = int(depth)
        if not self.engine:
            return
        # Turn OFF strength limiting for pure-depth mode
        try:
            self.engine.update_engine_parameters({"UCI_LimitStrength": "false"})
        except Exception:
            pass
        self.engine.set_depth(self.depth)
        self._elo_mode = False
        self.elo = None

    def set_elo(self, elo: int):
        """Elo-limited (weaker like chess.com bots), enables UCI_LimitStrength."""
        self.elo = int(elo)
        if not self.engine:
            return
        # Use the documented helper first
        try:
            self.engine.set_elo_rating(self.elo)   # wrapper sets UCI_LimitStrength internally
        except Exception:
            # Fallback: set options directly
            self.engine.update_engine_parameters({"UCI_LimitStrength": "true", "UCI_Elo": self.elo})
        self._elo_mode = True

    def set_skill(self, skill: int):
        """Alternative weakening (0..20)."""
        if not self.engine:
            return
        s = max(0, min(20, int(skill)))
        self.engine.set_skill_level(s)
        # Skill and Elo can coexist, but usually you use one or the other.
        self._elo_mode = False
        self.elo = None

    def get_best_move(self, board_fen):
        if not self.engine:
            return None
        try:
            self.engine.set_fen_position(board_fen)
            # Re-assert current mode before each search (defensive)
            if self._elo_mode and self.elo is not None:
                try:
                    self.engine.set_elo_rating(self.elo)
                except Exception:
                    self.engine.update_engine_parameters({"UCI_LimitStrength": "true", "UCI_Elo": self.elo})
            else:
                self.engine.update_engine_parameters({"UCI_LimitStrength": "false"})
                self.engine.set_depth(self.depth)

            # Use timed search for 3 seconds to avoid instant moves
            return self.engine.get_best_move_time(3000)  # 3000ms = 3 seconds
        except Exception as e:
            print(f"Error getting best move: {e}")
            return None

    def get_evaluation(self, board_fen):
        if not self.engine:
            return 0
        try:
            self.engine.set_fen_position(board_fen)
            ev = self.engine.get_evaluation()
            if ev["type"] == "cp":
                return ev["value"] / 100.0
            if ev["type"] == "mate":
                return 999 if ev["value"] > 0 else -999
            return 0
        except Exception as e:
            print(f"Error getting evaluation: {e}")
            return 0
