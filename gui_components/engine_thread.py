import chess
from PyQt5.QtCore import QThread, pyqtSignal


class EngineThread(QThread):
    move_found = pyqtSignal(object)
    
    def __init__(self, engine, board_fen):
        super().__init__()
        self.engine = engine
        self.board_fen = board_fen

    def run(self):
        best_move_uci = self.engine.get_best_move(self.board_fen)
        if best_move_uci:
            try:
                move = chess.Move.from_uci(best_move_uci)
                self.move_found.emit(move)
            except:
                self.move_found.emit(None)
        else:
            self.move_found.emit(None)