#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QPalette, QFont, QDrag, QPixmap, QPainter
from PyQt5.QtCore import QMimeData, QPoint

class ScrabbleTile(QLabel):
    """A draggable Scrabble tile."""
    
    def __init__(self, letter, value, parent=None):
        super().__init__(parent)
        self.letter = letter.upper()
        self.value = value
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(40, 40)
        self.setMaximumSize(40, 40)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet("""
            background-color: #F7D794;
            color: #2C3A47;
            border: 1px solid #2C3A47;
            border-radius: 4px;
            font-weight: bold;
        """)
        self.update_text()
    
    def update_text(self):
        """Update the displayed text of the tile."""
        self.setText(f"{self.letter}\n{self.value}")
        self.setFont(QFont("Arial", 12, QFont.Bold))
    
    def mousePressEvent(self, event):
        """Handle mouse press event for drag and drop."""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move event for drag and drop."""
        if not (event.buttons() & Qt.LeftButton):
            return
        
        # Calculate distance
        distance = (event.pos() - self.drag_start_position).manhattanLength()
        if distance < 10:  # Minimum distance for drag
            return
        
        # Create drag object
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(f"{self.letter},{self.value}")
        drag.setMimeData(mime_data)
        
        # Create pixmap for drag representation
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        self.render(painter)
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
        
        # Execute drag
        drag.exec_(Qt.MoveAction)

class BoardCell(QLabel):
    """A cell on the Scrabble board."""
    
    # Define bonus types
    NORMAL = 0
    DOUBLE_LETTER = 1
    TRIPLE_LETTER = 2
    DOUBLE_WORD = 3
    TRIPLE_WORD = 4
    
    # Map bonus types to colors and text
    BONUS_STYLES = {
        NORMAL: {"bg": "#E5E5E5", "text": ""},
        DOUBLE_LETTER: {"bg": "#7FCCEF", "text": "DL"},
        TRIPLE_LETTER: {"bg": "#0097E6", "text": "TL"},
        DOUBLE_WORD: {"bg": "#F5C3C2", "text": "DW"},
        TRIPLE_WORD: {"bg": "#E83350", "text": "TW"}
    }
    
    tile_placed = pyqtSignal(int, int, str, int)  # row, col, letter, value
    tile_removed = pyqtSignal(int, int)  # row, col
    
    def __init__(self, row, col, bonus_type=NORMAL, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.bonus_type = bonus_type
        self.tile = None
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(44, 44)
        self.setMaximumSize(44, 44)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        # Apply bonus style
        self.apply_bonus_style()
    
    def apply_bonus_style(self):
        """Apply the visual style based on the bonus type."""
        style = self.BONUS_STYLES[self.bonus_type]
        self.setStyleSheet(f"""
            background-color: {style['bg']};
            color: #333333;
            border: 1px solid #CCCCCC;
            font-weight: bold;
            font-size: 10px;
        """)
        self.setText(style['text'])
    
    def set_bonus_type(self, bonus_type):
        """Set the bonus type of this cell."""
        if self.tile is None:  # Only change if no tile is present
            self.bonus_type = bonus_type
            self.apply_bonus_style()
    
    def has_tile(self):
        """Check if this cell has a tile."""
        return self.tile is not None
    
    def place_tile(self, letter, value):
        """Place a tile on this cell."""
        if self.tile:
            return False
        
        self.tile = ScrabbleTile(letter, value, self)
        self.tile.setParent(self)
        self.tile.show()
        
        # Center the tile in the cell
        self.tile.move(
            (self.width() - self.tile.width()) // 2,
            (self.height() - self.tile.height()) // 2
        )
        
        # Emit signal
        self.tile_placed.emit(self.row, self.col, letter, value)
        
        return True
    
    def remove_tile(self):
        """Remove the tile from this cell."""
        if self.tile:
            self.tile.deleteLater()
            self.tile = None
            self.tile_removed.emit(self.row, self.col)
            self.apply_bonus_style()
            return True
        return False
    
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if not self.tile and event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop event."""
        if event.mimeData().hasText():
            text = event.mimeData().text()
            try:
                letter, value = text.split(',')
                self.place_tile(letter, int(value))
                event.accept()
            except ValueError:
                event.ignore()
        else:
            event.ignore()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click to remove a tile."""
        if self.tile:
            self.remove_tile()

class GameBoardWidget(QWidget):
    """Widget for the Scrabble game board."""
    
    # Signals
    tile_placed = pyqtSignal(int, int, str, int)  # row, col, letter, value
    tile_removed = pyqtSignal(int, int)  # row, col
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.board_size = 15  # Standard Scrabble board is 15x15
        self.cells = []
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QGridLayout(self)
        layout.setSpacing(1)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create row labels (1-15)
        for i in range(self.board_size):
            label = QLabel(str(i + 1))
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label, i + 1, 0)
        
        # Create column labels (A-O)
        for i in range(self.board_size):
            label = QLabel(chr(65 + i))  # ASCII 'A' starts at 65
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label, 0, i + 1)
        
        # Create board cells
        self.cells = []
        for row in range(self.board_size):
            self.cells.append([])
            for col in range(self.board_size):
                bonus_type = self.get_default_bonus_type(row, col)
                cell = BoardCell(row, col, bonus_type)
                
                # Connect signals
                cell.tile_placed.connect(self.on_tile_placed)
                cell.tile_removed.connect(self.on_tile_removed)
                
                layout.addWidget(cell, row + 1, col + 1)
                self.cells[row].append(cell)
        
        self.setLayout(layout)
    
    def get_default_bonus_type(self, row, col):
        """Get the default bonus type for a cell position."""
        # Center (star) cell
        if row == 7 and col == 7:
            return BoardCell.DOUBLE_WORD
        
        # Triple word score
        if (row == 0 or row == 14) and (col == 0 or col == 7 or col == 14):
            return BoardCell.TRIPLE_WORD
        if (row == 7 and (col == 0 or col == 14)):
            return BoardCell.TRIPLE_WORD
        
        # Double word score
        if row == col or row + col == 14:
            if row > 0 and row < 14 and row != 7:
                return BoardCell.DOUBLE_WORD
        
        # Triple letter score
        if ((row == 1 or row == 13) and (col == 5 or col == 9)):
            return BoardCell.TRIPLE_LETTER
        if ((row == 5 or row == 9) and (col == 1 or col == 5 or col == 9 or col == 13)):
            return BoardCell.TRIPLE_LETTER
        
        # Double letter score
        if ((row == 0 or row == 14) and (col == 3 or col == 11)):
            return BoardCell.DOUBLE_LETTER
        if ((row == 2 or row == 12) and (col == 6 or col == 8)):
            return BoardCell.DOUBLE_LETTER
        if ((row == 3 or row == 11) and (col == 0 or col == 7 or col == 14)):
            return BoardCell.DOUBLE_LETTER
        if ((row == 6 or row == 8) and (col == 2 or col == 6 or col == 8 or col == 12)):
            return BoardCell.DOUBLE_LETTER
        if ((row == 7) and (col == 3 or col == 11)):
            return BoardCell.DOUBLE_LETTER
        
        return BoardCell.NORMAL
    
    def initialize_board(self, board_state=None):
        """Initialize the board with a given state or default state."""
        # Clear the board first
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.cells[row][col].has_tile():
                    self.cells[row][col].remove_tile()
        
        # If a board state is provided, set it up
        if board_state:
            for row in range(self.board_size):
                for col in range(self.board_size):
                    tile_info = board_state.get((row, col))
                    if tile_info:
                        letter, value = tile_info
                        self.cells[row][col].place_tile(letter, value)
    
    def update_board(self, board_updates):
        """Update the board with a list of updates."""
        for update in board_updates:
            row, col, action = update[0], update[1], update[2]
            
            if action == 'place':
                letter, value = update[3], update[4]
                self.cells[row][col].place_tile(letter, value)
            elif action == 'remove':
                self.cells[row][col].remove_tile()
            elif action == 'bonus':
                bonus_type = update[3]
                self.cells[row][col].set_bonus_type(bonus_type)
    
    def get_board_state(self):
        """Get the current state of the board."""
        state = {}
        for row in range(self.board_size):
            for col in range(self.board_size):
                cell = self.cells[row][col]
                if cell.has_tile():
                    # Get tile data from the cell
                    tile = cell.tile
                    state[(row, col)] = (tile.letter, tile.value)
        return state
    
    def on_tile_placed(self, row, col, letter, value):
        """Handle a tile being placed on the board."""
        self.tile_placed.emit(row, col, letter, value)
    
    def on_tile_removed(self, row, col):
        """Handle a tile being removed from the board."""
        self.tile_removed.emit(row, col)
    
    def is_empty(self):
        """Check if the board is empty."""
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.cells[row][col].has_tile():
                    return False
        return True
    
    def randomize_bonus_positions(self):
        """Randomize the positions of bonus cells."""
        import random
        
        # Count current bonuses by type
        bonus_counts = {
            BoardCell.DOUBLE_LETTER: 0,
            BoardCell.TRIPLE_LETTER: 0,
            BoardCell.DOUBLE_WORD: 0,
            BoardCell.TRIPLE_WORD: 0
        }
        
        # Count current bonuses
        for row in range(self.board_size):
            for col in range(self.board_size):
                bonus_type = self.cells[row][col].bonus_type
                if bonus_type != BoardCell.NORMAL:
                    bonus_counts[bonus_type] += 1
        
        # Reset all cells to normal
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.cells[row][col].set_bonus_type(BoardCell.NORMAL)
        
        # Set the center cell to double word
        self.cells[7][7].set_bonus_type(BoardCell.DOUBLE_WORD)
        bonus_counts[BoardCell.DOUBLE_WORD] -= 1
        
        # Keep track of assigned cells
        assigned_cells = set([(7, 7)])
        
        # Randomly assign bonus positions
        for bonus_type, count in bonus_counts.items():
            for _ in range(count):
                while True:
                    row = random.randint(0, self.board_size - 1)
                    col = random.randint(0, self.board_size - 1)
                    
                    # Check if the cell has already been assigned a bonus
                    if (row, col) not in assigned_cells:
                        self.cells[row][col].set_bonus_type(bonus_type)
                        assigned_cells.add((row, col))
                        break 