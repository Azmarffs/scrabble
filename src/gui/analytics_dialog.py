#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QLabel, QListWidget, QListWidgetItem, QWidget,
                           QPushButton, QGridLayout, QTableWidget, QTableWidgetItem,
                           QHeaderView, QComboBox, QGroupBox, QFrame, QSplitter)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QLinearGradient

class AnalyticsDialog(QDialog):
    """Dialog for displaying game analytics and statistics."""
    
    def __init__(self, db_manager, player, parent=None):
        """Initialize the analytics dialog.
        
        Args:
            db_manager: The database manager.
            player: The current player (or None if no player selected).
            parent: The parent widget.
        """
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.player = player
        self.current_stats = None
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Game Analytics")
        self.setMinimumSize(800, 600)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Player Stats tab
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        
        # Player selection if no player is provided
        if not self.player:
            selection_layout = QHBoxLayout()
            
            selection_layout.addWidget(QLabel("Select Player:"))
            
            self.player_combo = QComboBox()
            self.player_combo.currentIndexChanged.connect(self.player_changed)
            selection_layout.addWidget(self.player_combo)
            
            stats_layout.addLayout(selection_layout)
        else:
            # Display player name
            player_name = QLabel(f"Player: {self.player.name}")
            player_name.setFont(QFont("Arial", 14, QFont.Bold))
            stats_layout.addWidget(player_name)
        
        # Stats overview section
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        stats_frame.setLineWidth(1)
        
        stats_grid = QGridLayout(stats_frame)
        
        # Stats labels
        self.games_played_label = QLabel("0")
        self.wins_label = QLabel("0")
        self.losses_label = QLabel("0")
        self.win_rate_label = QLabel("0%")
        self.total_score_label = QLabel("0")
        self.avg_score_label = QLabel("0")
        self.highest_score_label = QLabel("0")
        self.avg_word_length_label = QLabel("0")
        
        # Style the labels
        stats_value_style = """
            font-size: 18px;
            font-weight: bold;
            color: #2980b9;
        """
        
        self.games_played_label.setStyleSheet(stats_value_style)
        self.wins_label.setStyleSheet(stats_value_style)
        self.losses_label.setStyleSheet(stats_value_style)
        self.win_rate_label.setStyleSheet(stats_value_style)
        self.total_score_label.setStyleSheet(stats_value_style)
        self.avg_score_label.setStyleSheet(stats_value_style)
        self.highest_score_label.setStyleSheet(stats_value_style)
        self.avg_word_length_label.setStyleSheet(stats_value_style)
        
        # Add stats to grid
        stats_grid.addWidget(QLabel("Games Played:"), 0, 0)
        stats_grid.addWidget(self.games_played_label, 0, 1)
        
        stats_grid.addWidget(QLabel("Wins:"), 1, 0)
        stats_grid.addWidget(self.wins_label, 1, 1)
        
        stats_grid.addWidget(QLabel("Losses:"), 2, 0)
        stats_grid.addWidget(self.losses_label, 2, 1)
        
        stats_grid.addWidget(QLabel("Win Rate:"), 3, 0)
        stats_grid.addWidget(self.win_rate_label, 3, 1)
        
        stats_grid.addWidget(QLabel("Total Score:"), 0, 2)
        stats_grid.addWidget(self.total_score_label, 0, 3)
        
        stats_grid.addWidget(QLabel("Average Score:"), 1, 2)
        stats_grid.addWidget(self.avg_score_label, 1, 3)
        
        stats_grid.addWidget(QLabel("Highest Score:"), 2, 2)
        stats_grid.addWidget(self.highest_score_label, 2, 3)
        
        stats_grid.addWidget(QLabel("Average Word Length:"), 3, 2)
        stats_grid.addWidget(self.avg_word_length_label, 3, 3)
        
        stats_layout.addWidget(stats_frame)
        
        # Recent games section
        recent_games_group = QGroupBox("Recent Games")
        recent_games_layout = QVBoxLayout(recent_games_group)
        
        self.games_table = QTableWidget()
        self.games_table.setColumnCount(6)
        self.games_table.setHorizontalHeaderLabels(["Date", "Score", "AI Score", "Winner", "Difficulty", "Duration"])
        self.games_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        recent_games_layout.addWidget(self.games_table)
        stats_layout.addWidget(recent_games_group)
        
        # Add stats tab to tab widget
        tab_widget.addTab(stats_tab, "Player Stats")
        
        # Word Stats tab
        words_tab = QWidget()
        words_layout = QVBoxLayout(words_tab)
        
        # Top words section
        top_words_group = QGroupBox("Top Words")
        top_words_layout = QVBoxLayout(top_words_group)
        
        self.top_words_table = QTableWidget()
        self.top_words_table.setColumnCount(3)
        self.top_words_table.setHorizontalHeaderLabels(["Word", "Score", "Times Used"])
        self.top_words_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        top_words_layout.addWidget(self.top_words_table)
        words_layout.addWidget(top_words_group)
        
        # Word length distribution
        word_length_group = QGroupBox("Word Length Distribution")
        word_length_layout = QVBoxLayout(word_length_group)
        
        # Simple bar chart using labels
        self.word_length_chart = QFrame()
        self.word_length_chart.setMinimumHeight(150)
        self.word_length_chart.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        
        word_length_chart_layout = QHBoxLayout(self.word_length_chart)
        word_length_chart_layout.setSpacing(2)
        word_length_chart_layout.setAlignment(Qt.AlignBottom)
        
        # Create bar labels (filled dynamically when loading data)
        self.word_length_bars = []
        for i in range(15):  # Maximum word length in Scrabble is 15
            bar = QFrame()
            bar.setFrameStyle(QFrame.Panel | QFrame.Raised)
            bar.setMinimumWidth(15)
            bar.setMaximumWidth(30)
            bar.setMinimumHeight(10)  # Will be updated with data
            
            # Set gradient color
            color = QColor(41, 128, 185)  # Blue
            color.setAlpha(100 + i * 10)  # Increase alpha with length
            
            bar.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #2980B9;")
            
            word_length_chart_layout.addWidget(bar)
            self.word_length_bars.append(bar)
        
        # X-axis labels
        x_labels_layout = QHBoxLayout()
        x_labels_layout.setSpacing(2)
        x_labels_layout.setAlignment(Qt.AlignBottom)
        
        for i in range(15):
            label = QLabel(str(i + 1))
            label.setAlignment(Qt.AlignCenter)
            x_labels_layout.addWidget(label)
        
        word_length_layout.addWidget(self.word_length_chart)
        word_length_layout.addLayout(x_labels_layout)
        words_layout.addWidget(word_length_group)
        
        # Add words tab to tab widget
        tab_widget.addTab(words_tab, "Word Stats")
        
        # Add tab widget to main layout
        main_layout.addWidget(tab_widget)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
    
    def load_data(self):
        """Load statistics data from the database."""
        if not self.player:
            # Load player list
            self.db_manager.connect()
            self.db_manager.cursor.execute("SELECT id, name FROM players ORDER BY name")
            players = self.db_manager.cursor.fetchall()
            self.db_manager.close()
            
            for player_id, player_name in players:
                self.player_combo.addItem(player_name, player_id)
        else:
            # Load player stats
            self.load_player_stats(self.player.id)
    
    def player_changed(self, index):
        """Handle player selection change.
        
        Args:
            index: The index of the selected player.
        """
        if index >= 0:
            player_id = self.player_combo.itemData(index)
            self.load_player_stats(player_id)
    
    def load_player_stats(self, player_id):
        """Load statistics for a specific player.
        
        Args:
            player_id: The ID of the player.
        """
        # Get player stats
        stats = self.db_manager.get_player_stats(player_id)
        if not stats:
            return
        
        self.current_stats = stats
        
        # Update stats labels
        player_info = stats['player']
        player_stats = stats['stats']
        
        games_played = player_stats[0] or 0
        self.games_played_label.setText(str(games_played))
        
        wins = player_stats[3] or 0
        self.wins_label.setText(str(wins))
        
        losses = player_stats[4] or 0
        self.losses_label.setText(str(losses))
        
        if games_played > 0:
            win_rate = (wins / games_played) * 100
            self.win_rate_label.setText(f"{win_rate:.1f}%")
        else:
            self.win_rate_label.setText("0%")
        
        total_score = player_stats[1] or 0
        self.total_score_label.setText(str(total_score))
        
        if games_played > 0:
            avg_score = total_score / games_played
            self.avg_score_label.setText(f"{avg_score:.1f}")
        else:
            self.avg_score_label.setText("0")
        
        highest_score = player_stats[2] or 0
        self.highest_score_label.setText(str(highest_score))
        
        # Load recent games
        self.db_manager.connect()
        self.db_manager.cursor.execute("""
        SELECT date_played, player_score, ai_score, winner, ai_difficulty, duration
        FROM games
        WHERE player_id = ?
        ORDER BY date_played DESC
        LIMIT 10
        """, (player_id,))
        recent_games = self.db_manager.cursor.fetchall()
        self.db_manager.close()
        
        # Update recent games table
        self.games_table.setRowCount(len(recent_games))
        
        for row, game in enumerate(recent_games):
            date = game[0].split(" ")[0]  # Just get the date part
            self.games_table.setItem(row, 0, QTableWidgetItem(date))
            self.games_table.setItem(row, 1, QTableWidgetItem(str(game[1])))
            self.games_table.setItem(row, 2, QTableWidgetItem(str(game[2])))
            
            winner_item = QTableWidgetItem(game[3].title())
            if game[3].lower() == "player":
                winner_item.setForeground(QBrush(QColor(39, 174, 96)))  # Green
            else:
                winner_item.setForeground(QBrush(QColor(231, 76, 60)))  # Red
                
            self.games_table.setItem(row, 3, winner_item)
            
            self.games_table.setItem(row, 4, QTableWidgetItem(game[4].title()))
            
            # Format duration
            minutes, seconds = divmod(game[5] or 0, 60)
            duration = f"{minutes}m {seconds}s"
            self.games_table.setItem(row, 5, QTableWidgetItem(duration))
        
        # Load word stats
        self.db_manager.connect()
        self.db_manager.cursor.execute("""
        SELECT word, score, COUNT(*) as uses
        FROM moves
        WHERE player_id = ?
        GROUP BY word
        ORDER BY score DESC, uses DESC
        LIMIT 20
        """, (player_id,))
        top_words = self.db_manager.cursor.fetchall()
        
        # Calculate average word length
        self.db_manager.cursor.execute("""
        SELECT AVG(LENGTH(word)) as avg_length
        FROM moves
        WHERE player_id = ?
        """, (player_id,))
        avg_length = self.db_manager.cursor.fetchone()
        
        if avg_length and avg_length[0]:
            self.avg_word_length_label.setText(f"{avg_length[0]:.1f}")
        else:
            self.avg_word_length_label.setText("0")
        
        # Get word length distribution
        self.db_manager.cursor.execute("""
        SELECT LENGTH(word) as length, COUNT(*) as count
        FROM moves
        WHERE player_id = ?
        GROUP BY length
        ORDER BY length
        """, (player_id,))
        word_length_dist = self.db_manager.cursor.fetchall()
        self.db_manager.close()
        
        # Update top words table
        self.top_words_table.setRowCount(len(top_words))
        
        for row, word_data in enumerate(top_words):
            self.top_words_table.setItem(row, 0, QTableWidgetItem(word_data[0]))
            self.top_words_table.setItem(row, 1, QTableWidgetItem(str(word_data[1])))
            self.top_words_table.setItem(row, 2, QTableWidgetItem(str(word_data[2])))
        
        # Update word length chart
        # First, reset all bars
        for bar in self.word_length_bars:
            bar.setMinimumHeight(10)
        
        # Get the maximum count for scaling
        max_count = 1
        if word_length_dist:
            max_count = max(count for _, count in word_length_dist)
        
        # Set bar heights proportional to counts
        for length, count in word_length_dist:
            if 1 <= length <= 15:  # Valid word lengths in Scrabble
                height = int((count / max_count) * 100) + 10  # Minimum height of 10
                self.word_length_bars[length - 1].setMinimumHeight(height)