import chess
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QWidget, QGraphicsDropShadowEffect, QPushButton
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtSvg import QSvgRenderer


class PromotionPieceButton(QWidget):
    """Borderless square that renders an SVG via QSvgRenderer (same as board)."""
    def __init__(self, renderer: "QSvgRenderer", square_size: int, on_click, hover_bg=True, parent=None):
        super().__init__(parent)
        self.renderer = renderer
        self.square_size = square_size
        self.on_click = on_click
        self.hover = False
        self.hover_bg = hover_bg
        self.setFixedSize(square_size, square_size)
        self.setMouseTracking(True)

    def enterEvent(self, _):
        self.hover = True
        self.update()

    def leaveEvent(self, _):
        self.hover = False
        self.update()

    def mousePressEvent(self, _):
        if callable(self.on_click):
            self.on_click()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        if self.hover and self.hover_bg:
            p.fillRect(self.rect(), QColor(240, 240, 240))
        # small padding like chess.com
        pad = max(4, int(self.square_size * 0.08))
        target = QRectF(pad, pad, self.square_size - 2*pad, self.square_size - 2*pad)
        self.renderer.render(p, target)
        p.end()


class PromotionDialog(QDialog):
    def __init__(self, parent=None, is_white=True, promotion_square=None, square_size=80):
        super().__init__(parent)
        self.piece = None
        self.is_white = is_white
        self.parent_widget = parent
        self.promotion_square = promotion_square
        self.square_size = square_size
        self.cancelled = False

        # frameless, translucent, shadow
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        card = QWidget(self)
        card.setObjectName("card")
        card.setStyleSheet("""
            #card {
                background: white;
                border-radius: 6px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)

        v = QVBoxLayout(card)
        v.setContentsMargins(4, 4, 4, 4)
        v.setSpacing(2)

        # use the SAME renderers as the board
        # board piece dict keys are "PNBRQKpnbrqk"
        board_widget = self.parent_widget
        renderers = board_widget.piece_renderers

        color_prefix = 'w' if is_white else 'b'
        order = [chess.QUEEN, chess.KNIGHT, chess.ROOK, chess.BISHOP]  # matches chess.com vertical example (Q, N, R, B)

        def symbol_for(pt):
            s = chess.piece_symbol(pt)
            ch = s.upper() if is_white else s.lower()
            return ch  # matches keys in piece_renderers

        # Buttons (vector-painted)
        for pt in order:
            renderer = renderers[symbol_for(pt)]
            btn = PromotionPieceButton(renderer, self.square_size, on_click=lambda p=pt: self.choose_piece(p))
            v.addWidget(btn)

        # tiny X like chess.com
        cancel = QPushButton("✕")
        cancel.setFixedSize(self.square_size, self.square_size // 2)
        cancel.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: #444;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover { background: #f0f0f0; }
        """)
        cancel.clicked.connect(self.cancel_promotion)
        v.addWidget(cancel)

        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        root.addWidget(card)

        total_h = self.square_size*4 + self.square_size//2 + 8
        self.setFixedSize(self.square_size + 8, total_h)

    def position_dialog(self):
        if not self.parent_widget or self.promotion_square is None:
            return

        board_widget = self.parent_widget
        display_square = self.promotion_square
        if hasattr(board_widget, 'main_window') and board_widget.main_window.board_flipped:
            display_square = 63 - self.promotion_square

        file = chess.square_file(display_square)
        rank = chess.square_rank(display_square)
        col, row = file, 7 - rank

        top_left = board_widget.mapToGlobal(board_widget.rect().topLeft())
        self.move(top_left.x() + col*self.square_size,
                  top_left.y() + row*self.square_size)

    def choose_piece(self, piece_type):
        self.piece = piece_type
        self.accept()

    def cancel_promotion(self):
        self.cancelled = True
        self.reject()


class ColorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = None
        self.setWindowTitle("Choose Your Color")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Which color would you like to play as?"))
        self.button_box = QDialogButtonBox()
        self.white_button = self.button_box.addButton("White", QDialogButtonBox.YesRole)
        self.black_button = self.button_box.addButton("Black", QDialogButtonBox.NoRole)
        layout.addWidget(self.button_box)
        self.white_button.clicked.connect(self.choose_white)
        self.black_button.clicked.connect(self.choose_black)

    def choose_white(self):
        self.color = chess.WHITE
        self.accept()

    def choose_black(self):
        self.color = chess.BLACK
        self.accept()