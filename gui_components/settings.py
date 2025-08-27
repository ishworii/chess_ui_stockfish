import os
from PyQt5.QtWidgets import QDialog, QTabWidget, QDialogButtonBox, QVBoxLayout, QWidget, QGroupBox, QHBoxLayout, QComboBox, QLabel
from PyQt5.QtCore import Qt
from .themes import BOARD_THEMES


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Settings")
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_appearance_tab(), "Appearance")
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_piece_themes(self):
        try:
            return [d for d in os.listdir("piece") if os.path.isdir(os.path.join("piece", d))]
        except FileNotFoundError:
            return []

    def create_appearance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        piece_group = QGroupBox("Piece Theme")
        piece_layout = QHBoxLayout(piece_group)
        self.piece_selector = QComboBox()
        self.piece_selector.addItems(self.get_piece_themes())
        self.piece_selector.setCurrentText(self.main_window.piece_theme)
        piece_layout.addWidget(self.piece_selector)
        layout.addWidget(piece_group)

        board_group = QGroupBox("Board Theme")
        board_layout = QHBoxLayout(board_group)
        self.board_selector = QComboBox()
        self.board_selector.addItems(BOARD_THEMES.keys())
        self.board_selector.setCurrentText(self.main_window.board_theme)
        board_layout.addWidget(self.board_selector)
        layout.addWidget(board_group)

        return tab