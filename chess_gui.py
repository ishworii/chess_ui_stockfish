import sys
import os
import chess
from stockfish_engine import StockfishEngine
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                           QVBoxLayout, QListWidget, QDialog, QPushButton, 
                           QInputDialog, QMessageBox)
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from gui_components.chessboard import ChessboardWidget
from gui_components.dialogs import ColorDialog
from gui_components.settings import SettingsDialog
from gui_components.engine_thread import EngineThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess")
        self.board = chess.Board()
        self.player_color = None
        self.board_flipped = False
        self.last_move = None
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.sound_player = QMediaPlayer()
        self.engine = StockfishEngine(depth=20)
        
        self.piece_theme = "cburnett"
        self.board_theme = "Default"

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        self.chessboard_widget = ChessboardWidget(self)
        layout.addWidget(self.chessboard_widget)

        right_panel = QVBoxLayout()
        layout.addLayout(right_panel)
        self.move_list = QListWidget()
        right_panel.addWidget(self.move_list)

        button_layout = QHBoxLayout()
        new_game_button = QPushButton("New Game")
        new_game_button.clicked.connect(self.start_new_game)
        button_layout.addWidget(new_game_button)

        fen_button = QPushButton("Load FEN")
        fen_button.clicked.connect(self.load_fen)
        button_layout.addWidget(fen_button)

        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.open_settings)
        button_layout.addWidget(settings_button)
        
        right_panel.addLayout(button_layout)

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Engine always plays at full strength - no changes needed
            self.piece_theme = dialog.piece_selector.currentText()
            self.board_theme = dialog.board_selector.currentText()
            self.chessboard_widget.load_pieces()
            self.chessboard_widget.update()

    def start_new_game(self):
        self.board.reset()
        self.move_list.clear()
        self.last_move = None
        self.chessboard_widget.update()
        self.start_game()

    def load_fen(self):
        fen, ok = QInputDialog.getText(self, "Load FEN", "Enter FEN string:")
        if ok and fen:
            try:
                self.board.set_fen(fen)
                self.move_list.clear()
                self.last_move = None
                self.chessboard_widget.update()
                self.start_game()
            except ValueError:
                print("Invalid FEN string")

    def start_game(self):
        if not self.engine.is_available():
            print("Stockfish engine is not available. Please install Stockfish binary.")
            return

        dialog = ColorDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.player_color = dialog.color
            self.board_flipped = self.player_color == chess.BLACK
            self.chessboard_widget.update()
            if self.board.turn != self.player_color:
                self.trigger_engine_move()
        else:
            self.close()

    def play_sound(self, sound_file):
        try:
            path = os.path.join(self.script_dir, sound_file)
            url = QUrl.fromLocalFile(os.path.abspath(path))
            # Stop any currently playing sound and reset
            self.sound_player.stop()
            self.sound_player.setMedia(QMediaContent(url))
            self.sound_player.setVolume(70)  # Consistent volume
            self.sound_player.play()
        except Exception as e:
            print(f"Could not play sound {sound_file}: {e}")

    def handle_move(self, move):
        is_capture = self.board.is_capture(move)
        is_castling = self.board.is_castling(move)
        is_promotion = move.promotion is not None

        if self.board.turn == chess.WHITE:
            san_move = self.board.san(move)
            self.move_list.addItem(f"{self.board.fullmove_number}. {san_move}")
        else:
            san_move = self.board.san(move)
            last_item = self.move_list.item(self.move_list.count() - 1)
            last_item.setText(f"{last_item.text()} {san_move}")

        self.board.push(move)
        self.last_move = move
        self.chessboard_widget.update()
        QApplication.processEvents()
        
        if self.board.is_game_over():
            self.play_sound("sound/game-end.mp3")
            self.show_game_end_dialog()
        elif is_promotion:
            self.play_sound("sound/promote.mp3")
        elif is_castling:
            self.play_sound("sound/castle.mp3")
        elif self.board.is_check():
            self.play_sound("sound/check.mp3")
        elif is_capture:
            self.play_sound("sound/capture.mp3")
        else:
            self.play_sound("sound/move.mp3")

        if not self.board.is_game_over() and self.board.turn != self.player_color:
            self.trigger_engine_move()

    def trigger_engine_move(self):
        self.engine_thread = EngineThread(self.engine, self.board.fen())
        self.engine_thread.move_found.connect(self.handle_engine_move)
        self.engine_thread.start()

    def handle_engine_move(self, move):
        if move:
            self.handle_move(move)

    def show_game_end_dialog(self):
        result = self.board.result()
        if result == "1-0":
            result_text = "White wins!"
        elif result == "0-1":
            result_text = "Black wins!"
        else:
            result_text = "Draw!"
        
        # Determine reason
        if self.board.is_checkmate():
            reason = "by checkmate"
        elif self.board.is_stalemate():
            reason = "by stalemate"
        elif self.board.is_insufficient_material():
            reason = "by insufficient material"
        elif self.board.is_seventyfive_moves():
            reason = "by 75-move rule"
        elif self.board.is_fivefold_repetition():
            reason = "by repetition"
        else:
            reason = ""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Game Over")
        msg.setText(f"{result_text}")
        if reason:
            msg.setInformativeText(reason)
        msg.setStandardButtons(QMessageBox.NoButton)
        
        # Add action buttons
        close_button = msg.addButton("Close", QMessageBox.RejectRole)
        rematch_button = msg.addButton("Rematch", QMessageBox.AcceptRole)
        fen_button = msg.addButton("Load FEN", QMessageBox.ActionRole)
        
        close_button.clicked.connect(self.close)
        rematch_button.clicked.connect(self.rematch)
        fen_button.clicked.connect(self.load_fen)
        
        msg.exec_()

    def rematch(self):
        """Start a new game with the same player color"""
        self.board.reset()
        self.move_list.clear()
        self.last_move = None
        self.chessboard_widget.update()
        # Start the game with the same color - no dialog needed
        if self.board.turn != self.player_color:
            self.trigger_engine_move()

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.start_new_game()
    sys.exit(app.exec_())