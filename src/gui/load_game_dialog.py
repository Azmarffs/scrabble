#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                           QCheckBox, QGroupBox, QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class LoadGameDialog(QDialog):
    """Dialog for loading saved games."""
    
    def __init__(self, db_manager, parent=None):
        """Initialize the load game dialog.
        
        Args:
            db_manager: The database manager.
            parent: The parent widget.
        """
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.selected_game_id = None
        
        self.init_ui()
        self.load_games()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Load Game")
        self.setMinimumSize(650, 400)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Select a Game to Load")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Filter controls
        filter_group = QGroupBox("Filter Games")
        filter_layout = QHBoxLayout(filter_group)
        
        # Player filter
        player_layout = QFormLayout()
        self.player_combo = QComboBox()
        self.player_combo.addItem("All Players", None)
        self.player_combo.currentIndexChanged.connect(self.apply_filters)
        player_layout.addRow("Player:", self.player_combo)
        filter_layout.addLayout(player_layout)
        
        # Status filter
        status_layout = QFormLayout()
        self.status_combo = QComboBox()
        self.status_combo.addItem("All Games", None)
        self.status_combo.addItem("Completed", True)
        self.status_combo.addItem("In Progress", False)
        self.status_combo.currentIndexChanged.connect(self.apply_filters)
        status_layout.addRow("Status:", self.status_combo)
        filter_layout.addLayout(status_layout)
        
        main_layout.addWidget(filter_group)
        
        # Games table
        self.games_table = QTableWidget()
        self.games_table.setColumnCount(7)
        self.games_table.setHorizontalHeaderLabels([
            "ID", "Date Played", "Player Score", "AI Score", 
            "Winner", "Duration", "Status"
        ])
        self.games_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.games_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.games_table.setSelectionMode(QTableWidget.SingleSelection)
        self.games_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.games_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Hide the ID column
        self.games_table.setColumnHidden(0, True)
        
        main_layout.addWidget(self.games_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        self.load_button = button_box.button(QDialogButtonBox.Ok)
        self.load_button.setText("Load")
        self.load_button.setEnabled(False)
        
        button_layout.addWidget(button_box)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def load_games(self):
        """Load the list of saved games from the database."""
        # Load players for filter
        self.db_manager.connect()
        self.db_manager.cursor.execute("SELECT id, name FROM players ORDER BY name")
        players = self.db_manager.cursor.fetchall()
        self.db_manager.close()
        
        # Populate player combo
        for player_id, player_name in players:
            self.player_combo.addItem(player_name, player_id)
        
        # Load games
        self.apply_filters()
    
    def apply_filters(self):
        """Apply filters and refresh the games list."""
        # Get filter values
        player_id = self.player_combo.currentData()
        completed = self.status_combo.currentData()
        
        # Get games based on filters
        games = self.db_manager.get_saved_games(player_id, completed)
        
        # Clear table
        self.games_table.setRowCount(0)
        
        # Add games to table
        for i, game in enumerate(games):
            self.games_table.insertRow(i)
            
            # ID (hidden)
            id_item = QTableWidgetItem(str(game[0]))
            self.games_table.setItem(i, 0, id_item)
            
            # Date Played
            date_item = QTableWidgetItem(game[7].split(" ")[0])  # Just show date part
            self.games_table.setItem(i, 1, date_item)
            
            # Player Score
            player_score_item = QTableWidgetItem(str(game[3]))
            self.games_table.setItem(i, 2, player_score_item)
            
            # AI Score
            ai_score_item = QTableWidgetItem(str(game[4]))
            self.games_table.setItem(i, 3, ai_score_item)
            
            # Winner
            winner_item = QTableWidgetItem(game[5].title() if game[5] else "In Progress")
            self.games_table.setItem(i, 4, winner_item)
            
            # Duration
            minutes, seconds = divmod(game[6] or 0, 60)
            duration_item = QTableWidgetItem(f"{minutes}m {seconds}s")
            self.games_table.setItem(i, 5, duration_item)
            
            # Status
            status_item = QTableWidgetItem("Completed" if game[9] else "In Progress")
            self.games_table.setItem(i, 6, status_item)
    
    def on_selection_changed(self):
        """Handle selection change in the games table."""
        selected_rows = self.games_table.selectedItems()
        if selected_rows:
            # Enable the load button
            self.load_button.setEnabled(True)
            
            # Get the game ID from the first column
            row = selected_rows[0].row()
            self.selected_game_id = int(self.games_table.item(row, 0).text())
        else:
            self.load_button.setEnabled(False)
            self.selected_game_id = None 