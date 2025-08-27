import chess
from PyQt5.QtWidgets import QWidget, QDialog
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtSvg import QSvgRenderer
from .themes import BOARD_THEMES
from .dialogs import PromotionDialog


class ChessboardWidget(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.square_size = 80
        self.setMinimumSize(self.square_size * 8, self.square_size * 8)
        self.piece_renderers = {}
        self.load_pieces()
        self.dragging = False
        self.drag_start_square = None
        self.drag_renderer = None
        self.drag_pos = None

    def load_pieces(self):
        piece_theme = self.main_window.piece_theme
        for piece_char in "PNBRQKpnbrqk":
            path = f"piece/{piece_theme}/{'w' if piece_char.isupper() else 'b'}{piece_char.lower()}.svg"
            self.piece_renderers[piece_char] = QSvgRenderer(path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        light_color, dark_color = BOARD_THEMES[self.main_window.board_theme]
        
        for row in range(8):
            for col in range(8):
                color = QColor(light_color) if (row + col) % 2 == 0 else QColor(dark_color)
                painter.fillRect(col * self.square_size, row * self.square_size, self.square_size, self.square_size, color)

        if self.main_window.last_move:
            highlight_color = QColor(255, 255, 0, 100)
            from_sq = self.main_window.last_move.from_square
            to_sq = self.main_window.last_move.to_square
            
            if self.main_window.board_flipped:
                from_sq = 63 - from_sq
                to_sq = 63 - to_sq

            painter.fillRect(chess.square_file(from_sq) * self.square_size, (7 - chess.square_rank(from_sq)) * self.square_size, self.square_size, self.square_size, highlight_color)
            painter.fillRect(chess.square_file(to_sq) * self.square_size, (7 - chess.square_rank(to_sq)) * self.square_size, self.square_size, self.square_size, highlight_color)

        # Draw legal move hints
        if self.drag_start_square is not None:
            legal_moves = [move for move in self.main_window.board.legal_moves if move.from_square == self.drag_start_square]
            for move in legal_moves:
                to_sq = move.to_square
                if self.main_window.board_flipped:
                    to_sq = 63 - to_sq
                
                row, col = 7 - chess.square_rank(to_sq), chess.square_file(to_sq)
                center_x = col * self.square_size + self.square_size / 2
                center_y = row * self.square_size + self.square_size / 2
                
                painter.setBrush(QColor(0, 0, 0, 50))
                painter.setPen(Qt.NoPen)

                if self.main_window.board.is_capture(move):
                    radius = self.square_size / 2
                    painter.drawEllipse(QRectF(center_x - radius, center_y - radius, 2 * radius, 2 * radius))
                    painter.setBrush(QColor(light_color) if (row + col) % 2 == 0 else QColor(dark_color))
                    radius = self.square_size / 2 * 0.80
                    painter.drawEllipse(QRectF(center_x - radius, center_y - radius, 2 * radius, 2 * radius))
                else:
                    radius = self.square_size / 6
                    painter.drawEllipse(QRectF(center_x - radius, center_y - radius, 2 * radius, 2 * radius))

        for square in chess.SQUARES:
            piece = self.main_window.board.piece_at(square)
            if piece and not (self.dragging and square == self.drag_start_square):
                renderer = self.piece_renderers[piece.symbol()]
                
                display_square = square
                if self.main_window.board_flipped:
                    display_square = 63 - square
                
                row, col = 7 - chess.square_rank(display_square), chess.square_file(display_square)
                renderer.render(painter, QRectF(col * self.square_size, row * self.square_size, self.square_size, self.square_size))
        
        if self.dragging and self.drag_renderer:
            self.drag_renderer.render(painter, QRectF(self.drag_pos.x(), self.drag_pos.y(), self.square_size, self.square_size))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.main_window.board.turn == self.main_window.player_color:
            square = self.square_from_pos(event.pos())
            piece = self.main_window.board.piece_at(square)
            if piece and piece.color == self.main_window.player_color:
                self.dragging = True
                self.drag_start_square = square
                self.drag_renderer = self.piece_renderers[piece.symbol()]
                self.drag_pos = event.pos() - QRectF(0, 0, self.square_size, self.square_size).center()
                self.update()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.drag_pos = event.pos() - QRectF(0, 0, self.square_size, self.square_size).center()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            to_square = self.square_from_pos(event.pos())
            move = chess.Move(self.drag_start_square, to_square)
            
            piece = self.main_window.board.piece_at(self.drag_start_square)
            if piece and piece.piece_type == chess.PAWN and (chess.square_rank(to_square) == 0 or chess.square_rank(to_square) == 7):
                promo_dialog = PromotionDialog(self, is_white=piece.color, promotion_square=to_square, square_size=self.square_size)
                promo_dialog.show()
                promo_dialog.position_dialog()
                if promo_dialog.exec_() == QDialog.Accepted and not promo_dialog.cancelled:
                    move.promotion = promo_dialog.piece
                elif promo_dialog.cancelled:
                    # Cancel the move if user clicked X
                    self.update()
                    return

            if move in self.main_window.board.legal_moves:
                self.main_window.handle_move(move)
            self.update()

    def square_from_pos(self, pos):
        square = chess.square(pos.x() // self.square_size, 7 - (pos.y() // self.square_size))
        if self.main_window.board_flipped:
            return 63 - square
        return square