#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QDrag, QPixmap, QPainter
from PyQt5.QtCore import QMimeData, QPoint

class RackTile(QLabel):
    """A draggable tile in the player's rack."""
    
    selected = pyqtSignal(str, int)  # letter, value
    
    def __init__(self, letter, value, parent=None):
        super().__init__(parent)
        self.letter = letter.upper()
        self.value = value
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(45, 45)
        self.setMaximumSize(45, 45)
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
        self.setFont(QFont("Arial", 14, QFont.Bold))
    
    def mousePressEvent(self, event):
        """Handle mouse press event for drag and drop."""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            self.selected.emit(self.letter, self.value)
    
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
    
    def set_selected(self, selected):
        """Set the selected state of the tile."""
        if selected:
            self.setStyleSheet("""
                background-color: #F7D794;
                color: #2C3A47;
                border: 2px solid #2980B9;
                border-radius: 4px;
                font-weight: bold;
            """)
        else:
            self.setStyleSheet("""
                background-color: #F7D794;
                color: #2C3A47;
                border: 1px solid #2C3A47;
                border-radius: 4px;
                font-weight: bold;
            """)

class PlayerRackWidget(QWidget):
    """Widget for displaying the player's tile rack."""
    
    # Signals
    tile_selected = pyqtSignal(str, int)  # letter, value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tiles = []
        self.max_tiles = 7  # Standard Scrabble rack holds 7 tiles
        self.selected_tile = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title label
        title_label = QLabel("Your Tiles")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # Create rack frame
        self.rack_frame = QFrame()
        self.rack_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.rack_frame.setLineWidth(2)
        self.rack_frame.setStyleSheet("background-color: #D6B88E;")
        
        # Rack layout
        self.rack_layout = QHBoxLayout(self.rack_frame)
        self.rack_layout.setContentsMargins(5, 5, 5, 5)
        self.rack_layout.setSpacing(5)
        self.rack_layout.setAlignment(Qt.AlignCenter)
        
        # Add empty spaces for tiles
        for i in range(self.max_tiles):
            empty_tile = QLabel()
            empty_tile.setMinimumSize(45, 45)
            empty_tile.setMaximumSize(45, 45)
            empty_tile.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
            self.rack_layout.addWidget(empty_tile)
        
        main_layout.addWidget(self.rack_frame)
        self.setLayout(main_layout)
    
    def update_rack(self, tiles):
        """Update the rack with a new set of tiles."""
        # Clear current tiles
        for tile in self.tiles:
            tile.deleteLater()
        
        self.tiles = []
        self.selected_tile = None
        
        # Remove empty spaces
        while self.rack_layout.count():
            item = self.rack_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new tiles
        for letter, value in tiles:
            tile = RackTile(letter, value, self)
            tile.selected.connect(self.on_tile_selected)
            self.rack_layout.addWidget(tile)
            self.tiles.append(tile)
        
        # Add empty spaces if needed
        for i in range(len(tiles), self.max_tiles):
            empty_tile = QLabel()
            empty_tile.setMinimumSize(45, 45)
            empty_tile.setMaximumSize(45, 45)
            empty_tile.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
            self.rack_layout.addWidget(empty_tile)
    
    def add_tile(self, letter, value):
        """Add a tile to the rack."""
        if len(self.tiles) < self.max_tiles:
            tile = RackTile(letter, value, self)
            tile.selected.connect(self.on_tile_selected)
            
            # Remove an empty space
            if self.rack_layout.count() > len(self.tiles):
                item = self.rack_layout.takeAt(len(self.tiles))
                if item.widget():
                    item.widget().deleteLater()
            
            self.rack_layout.addWidget(tile)
            self.tiles.append(tile)
            return True
        return False
    
    def remove_tile(self, letter):
        """Remove a tile with the given letter from the rack."""
        for i, tile in enumerate(self.tiles):
            if tile.letter == letter.upper():
                # Remove from the layout
                self.rack_layout.removeWidget(tile)
                tile.deleteLater()
                
                # Remove from our list
                self.tiles.pop(i)
                
                # Add an empty space
                empty_tile = QLabel()
                empty_tile.setMinimumSize(45, 45)
                empty_tile.setMaximumSize(45, 45)
                empty_tile.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
                self.rack_layout.addWidget(empty_tile)
                
                return True
        return False
    
    def get_tiles(self):
        """Get the current tiles in the rack."""
        return [(tile.letter, tile.value) for tile in self.tiles]
    
    def on_tile_selected(self, letter, value):
        """Handle a tile being selected."""
        # Reset all tiles
        for tile in self.tiles:
            tile.set_selected(False)
        
        # Find the selected tile
        for tile in self.tiles:
            if tile.letter == letter and tile.value == value:
                tile.set_selected(True)
                self.selected_tile = tile
                break
        
        self.tile_selected.emit(letter, value)
    
    def get_selected_tile(self):
        """Get the currently selected tile."""
        if self.selected_tile:
            return self.selected_tile.letter, self.selected_tile.value
        return None 