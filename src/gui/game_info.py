#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                            QProgressBar, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon

class GameInfoWidget(QWidget):
    """Widget for displaying game information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)  # Increased spacing between elements
        
        # Title
        title_label = QLabel("Game Information")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setMinimumHeight(30)  # Set minimum height
        main_layout.addWidget(title_label)
        
        # Frame for score info
        score_frame = QFrame()
        score_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        score_frame.setLineWidth(1)
        score_layout = QVBoxLayout(score_frame)
        score_layout.setContentsMargins(8, 8, 8, 8)  # Increased padding
        score_layout.setSpacing(8)  # Increased spacing
        
        # Player score
        player_score_layout = QHBoxLayout()
        player_label = QLabel("Your Score:")
        player_label.setFont(QFont("Arial", 10, QFont.Bold))
        player_label.setMinimumHeight(24)  # Set minimum height
        self.player_score_label = QLabel("0")
        self.player_score_label.setFont(QFont("Arial", 10))
        self.player_score_label.setMinimumHeight(24)  # Set minimum height
        player_score_layout.addWidget(player_label)
        player_score_layout.addWidget(self.player_score_label, 1)
        score_layout.addLayout(player_score_layout)
        
        # AI score
        ai_score_layout = QHBoxLayout()
        ai_label = QLabel("AI Score:")
        ai_label.setFont(QFont("Arial", 10, QFont.Bold))
        ai_label.setMinimumHeight(24)  # Set minimum height
        self.ai_score_label = QLabel("0")
        self.ai_score_label.setFont(QFont("Arial", 10))
        self.ai_score_label.setMinimumHeight(24)  # Set minimum height
        ai_score_layout.addWidget(ai_label)
        ai_score_layout.addWidget(self.ai_score_label, 1)
        score_layout.addLayout(ai_score_layout)
        
        # Difficulty
        difficulty_layout = QHBoxLayout()
        difficulty_label = QLabel("Difficulty:")
        difficulty_label.setFont(QFont("Arial", 10, QFont.Bold))
        difficulty_label.setMinimumHeight(24)  # Set minimum height
        self.difficulty_label = QLabel("Medium")
        self.difficulty_label.setFont(QFont("Arial", 10))
        self.difficulty_label.setMinimumHeight(24)  # Set minimum height
        difficulty_layout.addWidget(difficulty_label)
        difficulty_layout.addWidget(self.difficulty_label, 1)
        score_layout.addLayout(difficulty_layout)
        
        # Add score frame to main layout
        main_layout.addWidget(score_frame)
        
        # Turn indicator frame
        turn_frame = QFrame()
        turn_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        turn_frame.setLineWidth(1)
        turn_layout = QVBoxLayout(turn_frame)
        turn_layout.setContentsMargins(8, 8, 8, 8)  # Increased padding
        turn_layout.setSpacing(8)  # Increased spacing
        
        # Current turn
        current_turn_label = QLabel("Current Turn:")
        current_turn_label.setFont(QFont("Arial", 10, QFont.Bold))
        current_turn_label.setMinimumHeight(24)  # Set minimum height
        turn_layout.addWidget(current_turn_label)
        
        # Turn indicator
        self.turn_indicator = QLabel("Your Turn")
        self.turn_indicator.setAlignment(Qt.AlignCenter)
        self.turn_indicator.setFont(QFont("Arial", 12, QFont.Bold))
        self.turn_indicator.setMinimumHeight(30)  # Set minimum height
        self.turn_indicator.setStyleSheet("""
            background-color: #E6F7FF;
            color: #0066CC;
            border: 1px solid #0066CC;
            border-radius: 4px;
            padding: 8px;
            min-height: 30px;
        """)
        turn_layout.addWidget(self.turn_indicator)
        
        # Turn number
        turn_number_layout = QHBoxLayout()
        turn_number_label = QLabel("Turn Number:")
        turn_number_label.setFont(QFont("Arial", 10, QFont.Bold))
        turn_number_label.setMinimumHeight(24)  # Set minimum height
        self.turn_number_label = QLabel("1")
        self.turn_number_label.setFont(QFont("Arial", 10))
        self.turn_number_label.setMinimumHeight(24)  # Set minimum height
        turn_number_layout.addWidget(turn_number_label)
        turn_number_layout.addWidget(self.turn_number_label, 1)
        turn_layout.addLayout(turn_number_layout)
        
        # Tiles remaining
        tiles_remaining_layout = QHBoxLayout()
        tiles_remaining_label = QLabel("Tiles in Bag:")
        tiles_remaining_label.setFont(QFont("Arial", 10, QFont.Bold))
        tiles_remaining_label.setMinimumHeight(24)  # Set minimum height
        self.tiles_remaining_label = QLabel("86")  # 100 - 2 players * 7 tiles
        self.tiles_remaining_label.setFont(QFont("Arial", 10))
        self.tiles_remaining_label.setMinimumHeight(24)  # Set minimum height
        tiles_remaining_layout.addWidget(tiles_remaining_label)
        tiles_remaining_layout.addWidget(self.tiles_remaining_label, 1)
        turn_layout.addLayout(tiles_remaining_layout)
        
        # Add turn frame to main layout
        main_layout.addWidget(turn_frame)
        
        # Game progress frame
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        progress_frame.setLineWidth(1)
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(8, 8, 8, 8)  # Increased padding
        progress_layout.setSpacing(8)  # Increased spacing
        
        # Game progress label
        progress_label = QLabel("Game Progress:")
        progress_label.setFont(QFont("Arial", 10, QFont.Bold))
        progress_label.setMinimumHeight(24)  # Set minimum height
        progress_layout.addWidget(progress_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(24)  # Set minimum height
        progress_layout.addWidget(self.progress_bar)
        
        # Game time
        game_time_layout = QHBoxLayout()
        game_time_label = QLabel("Game Time:")
        game_time_label.setFont(QFont("Arial", 10, QFont.Bold))
        game_time_label.setMinimumHeight(24)  # Set minimum height
        self.game_time_label = QLabel("00:00")
        self.game_time_label.setFont(QFont("Arial", 10))
        self.game_time_label.setMinimumHeight(24)  # Set minimum height
        game_time_layout.addWidget(game_time_label)
        game_time_layout.addWidget(self.game_time_label, 1)
        progress_layout.addLayout(game_time_layout)
        
        # Add progress frame to main layout
        main_layout.addWidget(progress_frame)
        
        # Last move frame
        last_move_frame = QFrame()
        last_move_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        last_move_frame.setLineWidth(1)
        last_move_layout = QVBoxLayout(last_move_frame)
        last_move_layout.setContentsMargins(8, 8, 8, 8)  # Increased padding
        last_move_layout.setSpacing(8)  # Increased spacing
        
        # Last move title
        last_move_title = QLabel("Last Move:")
        last_move_title.setFont(QFont("Arial", 10, QFont.Bold))
        last_move_title.setMinimumHeight(24)  # Set minimum height
        last_move_layout.addWidget(last_move_title)
        
        # Last move info
        self.last_move_label = QLabel("None")
        self.last_move_label.setFont(QFont("Arial", 10))
        self.last_move_label.setWordWrap(True)
        self.last_move_label.setMinimumHeight(24)  # Set minimum height
        self.last_move_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Vertical alignment
        last_move_layout.addWidget(self.last_move_label)
        
        # Last move score
        last_move_score_layout = QHBoxLayout()
        last_move_score_label = QLabel("Score:")
        last_move_score_label.setFont(QFont("Arial", 10, QFont.Bold))
        last_move_score_label.setMinimumHeight(24)  # Set minimum height
        self.last_move_score_label = QLabel("0")
        self.last_move_score_label.setFont(QFont("Arial", 10))
        self.last_move_score_label.setMinimumHeight(24)  # Set minimum height
        last_move_score_layout.addWidget(last_move_score_label)
        last_move_score_layout.addWidget(self.last_move_score_label, 1)
        last_move_layout.addLayout(last_move_score_layout)
        
        # Add last move frame to main layout
        main_layout.addWidget(last_move_frame)
        
        # Add stretch to push everything to the top
        main_layout.addStretch(1)
        
        self.setLayout(main_layout)
    
    def update_info(self, game_info):
        """Update the game information."""
        # Update scores
        self.player_score_label.setText(str(game_info.get('player_score', 0)))
        self.ai_score_label.setText(str(game_info.get('ai_score', 0)))
        
        # Update difficulty
        self.difficulty_label.setText(game_info.get('difficulty', 'Medium').capitalize())
        
        # Update turn info
        is_player_turn = game_info.get('is_player_turn', True)
        if is_player_turn:
            self.turn_indicator.setText("Your Turn")
            self.turn_indicator.setStyleSheet("""
                background-color: #E6F7FF;
                color: #0066CC;
                border: 1px solid #0066CC;
                border-radius: 4px;
                padding: 8px;
                min-height: 30px;
            """)
        else:
            self.turn_indicator.setText("AI's Turn")
            self.turn_indicator.setStyleSheet("""
                background-color: #FFE6E6;
                color: #CC0000;
                border: 1px solid #CC0000;
                border-radius: 4px;
                padding: 8px;
                min-height: 30px;
            """)
        
        # Update turn number
        self.turn_number_label.setText(str(game_info.get('turn_number', 1)))
        
        # Update tiles remaining
        self.tiles_remaining_label.setText(str(game_info.get('tiles_remaining', 86)))
        
        # Update progress
        progress = game_info.get('progress', 0)
        self.progress_bar.setValue(progress)
        
        # Update game time
        game_time = game_info.get('game_time', '00:00')
        self.game_time_label.setText(game_time)
        
        # Update last move
        last_move = game_info.get('last_move', {'word': 'None', 'score': 0})
        self.last_move_label.setText(last_move.get('word', 'None'))
        self.last_move_score_label.setText(str(last_move.get('score', 0))) 