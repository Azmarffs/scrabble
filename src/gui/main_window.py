#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QMainWindow, QAction, QMenu, QWidget, QVBoxLayout, 
                           QHBoxLayout, QStackedWidget, QMessageBox, QLabel,
                           QPushButton, QDialog, QLineEdit, QFormLayout)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QSettings
from PyQt5.QtGui import QIcon, QFont, QPixmap

from src.gui.game_board import GameBoardWidget
from src.gui.player_rack import PlayerRackWidget
from src.gui.game_info import GameInfoWidget
from src.gui.settings_dialog import SettingsDialog
from src.gui.analytics_dialog import AnalyticsDialog
from src.gui.load_game_dialog import LoadGameDialog
from src.game.game_controller import GameController
from src.game.player import Player

class MainWindow(QMainWindow):
    """Main window for the Scrabble game application."""
    
    def __init__(self, db_manager):
        """Initialize the main window with the database manager."""
        super().__init__()
        
        self.db_manager = db_manager
        self.settings = QSettings()
        self.game_controller = None
        self.current_player = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Scrabble")
        self.setMinimumSize(1024, 768)
        
        # Set up the central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Set up the stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Create welcome screen
        self.create_welcome_screen()
        
        # Create game screen
        self.create_game_screen()
        
        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.game_screen)
        
        # Set up menus
        self.create_menus()
        
        # Show welcome screen by default
        self.stacked_widget.setCurrentIndex(0)
    
    def challenge_word(self):
        """Challenge the AI's last word."""
        if not self.game_controller:
            return

        last_move = self.game_controller.last_move
        if last_move['player'] != 'ai' or last_move['word'] == 'PASS':
            return

        result = self.game_controller.challenge_word(last_move['word'])
        
        if result:
            QMessageBox.information(
                self,
                "Challenge Successful",
                f"Challenge successful! The word '{last_move['word']}' was invalid.\n"
                f"Points have been deducted from AI's score."
            )
        else:
            QMessageBox.warning(
                self,
                "Challenge Failed",
                f"Challenge failed! The word '{last_move['word']}' is valid.\n"
                f"You have been penalized {self.game_controller.challenge_penalty} points."
            )
    
    def create_welcome_screen(self):
        """Create the welcome screen widget."""
        self.welcome_screen = QWidget()
        layout = QVBoxLayout(self.welcome_screen)
        layout.setAlignment(Qt.AlignCenter)
        
        # Title label
        title_label = QLabel("Scrabble")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 36, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Buttons layout
        buttons_layout = QVBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(20)
        
        # New game button
        new_game_btn = QPushButton("New Game")
        new_game_btn.setMinimumSize(200, 50)
        new_game_btn.clicked.connect(self.new_game_dialog)
        buttons_layout.addWidget(new_game_btn)
        
        # Load game button
        load_game_btn = QPushButton("Load Game")
        load_game_btn.setMinimumSize(200, 50)
        load_game_btn.clicked.connect(self.load_game)
        buttons_layout.addWidget(load_game_btn)
        
        # Settings button
        settings_btn = QPushButton("Settings")
        settings_btn.setMinimumSize(200, 50)
        settings_btn.clicked.connect(self.show_settings)
        buttons_layout.addWidget(settings_btn)
        
        # Analytics button
        analytics_btn = QPushButton("Analytics")
        analytics_btn.setMinimumSize(200, 50)
        analytics_btn.clicked.connect(self.show_analytics)
        buttons_layout.addWidget(analytics_btn)
        
        # Exit button
        exit_btn = QPushButton("Exit")
        exit_btn.setMinimumSize(200, 50)
        exit_btn.clicked.connect(self.close)
        buttons_layout.addWidget(exit_btn)
        
        layout.addLayout(buttons_layout)
    
    def create_game_screen(self):
        """Create the game screen widget."""
        self.game_screen = QWidget()
        layout = QHBoxLayout(self.game_screen)
        
        # Game board widget
        self.game_board = GameBoardWidget()
        
        # Right sidebar layout
        sidebar_layout = QVBoxLayout()
        
        # Game info widget
        self.game_info = GameInfoWidget()
        sidebar_layout.addWidget(self.game_info)
        
        # Player rack widget
        self.player_rack = PlayerRackWidget()
        sidebar_layout.addWidget(self.player_rack)
        
        # Game control buttons
        controls_layout = QHBoxLayout()
        
        self.submit_btn = QPushButton("Submit Move")
        self.submit_btn.clicked.connect(self.submit_move)
        controls_layout.addWidget(self.submit_btn)
        
        self.recall_btn = QPushButton("Recall Tiles")
        self.recall_btn.clicked.connect(self.recall_tiles)
        controls_layout.addWidget(self.recall_btn)
        
        self.pass_btn = QPushButton("Pass Turn")
        self.pass_btn.clicked.connect(self.pass_turn)
        controls_layout.addWidget(self.pass_btn)
        
        sidebar_layout.addLayout(controls_layout)
        
        # Add back to main menu button
        self.back_btn = QPushButton("Back to Menu")
        self.back_btn.clicked.connect(self.confirm_back_to_menu)
        sidebar_layout.addWidget(self.back_btn)
        
        # Add widgets to main layout
        layout.addWidget(self.game_board, 3)
        layout.addLayout(sidebar_layout, 1)
    
    def create_menus(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_game_action = QAction("New Game", self)
        new_game_action.triggered.connect(self.new_game_dialog)
        file_menu.addAction(new_game_action)
        
        load_game_action = QAction("Load Game", self)
        load_game_action.triggered.connect(self.load_game)
        file_menu.addAction(load_game_action)
        
        save_game_action = QAction("Save Game", self)
        save_game_action.triggered.connect(self.save_game)
        file_menu.addAction(save_game_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Game menu
        game_menu = menubar.addMenu("Game")
        
        pause_action = QAction("Pause", self)
        pause_action.triggered.connect(self.pause_game)
        game_menu.addAction(pause_action)
        
        restart_action = QAction("Restart", self)
        restart_action.triggered.connect(self.restart_game)
        game_menu.addAction(restart_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.show_settings)
        settings_menu.addAction(preferences_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        rules_action = QAction("Game Rules", self)
        rules_action.triggered.connect(self.show_rules)
        help_menu.addAction(rules_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def new_game_dialog(self):
        """Show dialog to create a new game."""
        dialog = QDialog(self)
        dialog.setWindowTitle("New Game")
        layout = QFormLayout(dialog)
        
        # Player name input
        player_name_input = QLineEdit()
        player_name_input.setText(self.settings.value("player_name", ""))
        layout.addRow("Player Name:", player_name_input)
        
        # Difficulty selection
        difficulty_options = ["Easy", "Medium", "Hard"]
        difficulty_buttons = []
        difficulty_layout = QHBoxLayout()
        
        for difficulty in difficulty_options:
            btn = QPushButton(difficulty)
            btn.setCheckable(True)
            if difficulty.lower() == self.settings.value("ai_difficulty", "medium"):
                btn.setChecked(True)
            difficulty_buttons.append(btn)
            difficulty_layout.addWidget(btn)
            
            # Connect button to close dialog and start game
            btn.clicked.connect(
                lambda checked, d=difficulty, pn=player_name_input: 
                self.start_new_game(pn.text(), d.lower()) or dialog.accept()
            )
        
        layout.addRow("AI Difficulty:", difficulty_layout)
        
        dialog.exec_()
    
    def start_new_game(self, player_name, difficulty):
        """Start a new game with the given player name and difficulty."""
        if not player_name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a player name.")
            return False
        
        # Save player name and difficulty in settings
        self.settings.setValue("player_name", player_name)
        self.settings.setValue("ai_difficulty", difficulty)
        
        # Create or get player from database
        self.db_manager.connect()
        self.db_manager.cursor.execute(
            "SELECT id FROM players WHERE name = ?", (player_name,)
        )
        player_data = self.db_manager.cursor.fetchone()
        
        if player_data:
            player_id = player_data[0]
        else:
            self.db_manager.cursor.execute(
                "INSERT INTO players (name) VALUES (?)", (player_name,)
            )
            player_id = self.db_manager.cursor.lastrowid
        
        self.db_manager.commit()
        self.db_manager.close()
        
        # Create player object
        self.current_player = Player(player_id, player_name, is_ai=False)
        
        # Create game controller
        self.game_controller = GameController(
            self.db_manager, 
            self.current_player,
            difficulty
        )
        
        # Connect signals
        self.connect_game_signals()
        
        # Initialize game
        self.game_controller.initialize_game()
        
        # Update UI
        self.update_game_ui()
        
        # Switch to game screen
        self.stacked_widget.setCurrentIndex(1)
        
        return True
    
    def connect_game_signals(self):
        """Connect signals between game controller and UI components."""
        # Connect game board signals
        self.game_board.tile_placed.connect(self.game_controller.place_tile)
        self.game_board.tile_removed.connect(self.game_controller.remove_tile)
        
        # Connect player rack signals
        self.player_rack.tile_selected.connect(self.game_controller.select_tile)
        
        # Connect game controller signals
        self.game_controller.board_updated.connect(self.game_board.update_board)
        self.game_controller.rack_updated.connect(self.player_rack.update_rack)
        self.game_controller.game_info_updated.connect(self.game_info.update_info)
        self.game_controller.move_result.connect(self.show_move_result)
        self.game_controller.game_over.connect(self.show_game_over)
    
    def update_game_ui(self):
        """Update the game UI components."""
        # Update game board
        self.game_board.initialize_board(self.game_controller.get_board_state())
        
        # Update player rack
        self.player_rack.update_rack(self.game_controller.get_player_tiles())
        
        # Update game info
        self.game_info.update_info(
            self.game_controller.get_game_info()
        )
    
    def submit_move(self):
        """Submit the current move."""
        self.game_controller.submit_move()
    
    def recall_tiles(self):
        """Recall all tiles from the board back to the rack."""
        self.game_controller.recall_tiles()
    
    def pass_turn(self):
        """Pass the current turn."""
        self.game_controller.pass_turn()
    
    def load_game(self):
        """Show dialog to load a saved game."""
        dialog = LoadGameDialog(self.db_manager, self)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_game_id:
            self.load_game_by_id(dialog.selected_game_id)
    
    def load_game_by_id(self, game_id):
        """Load a game by its ID."""
        game_data = self.db_manager.load_game(game_id)
        if game_data:
            # Get player info
            self.db_manager.connect()
            self.db_manager.cursor.execute(
                "SELECT id, name FROM players WHERE id = ?", 
                (game_data['game'][1],)  # player_id is at index 1
            )
            player_data = self.db_manager.cursor.fetchone()
            self.db_manager.close()
            
            if player_data:
                # Create player object
                self.current_player = Player(player_data[0], player_data[1], is_ai=False)
                
                # Create game controller
                self.game_controller = GameController(
                    self.db_manager,
                    self.current_player,
                    game_data['game'][2]  # ai_difficulty is at index 2
                )
                
                # Connect signals
                self.connect_game_signals()
                
                # Load game state
                self.game_controller.load_game(game_data)
                
                # Update UI
                self.update_game_ui()
                
                # Switch to game screen
                self.stacked_widget.setCurrentIndex(1)
                
                return True
        
        QMessageBox.warning(self, "Load Failed", "Failed to load the selected game.")
        return False
    
    def save_game(self):
        """Save the current game."""
        if not self.game_controller:
            return
        
        game_id = self.game_controller.save_game()
        if game_id:
            QMessageBox.information(
                self, "Game Saved", f"Game saved successfully (ID: {game_id})."
            )
        else:
            QMessageBox.warning(
                self, "Save Failed", "Failed to save the game."
            )
    
    def pause_game(self):
        """Pause the current game."""
        if self.game_controller:
            self.game_controller.pause_game()
            QMessageBox.information(
                self, "Game Paused", "Game is paused. Click OK to resume."
            )
            self.game_controller.resume_game()
    
    def restart_game(self):
        """Restart the current game."""
        if not self.game_controller:
            return
        
        reply = QMessageBox.question(
            self, "Restart Game", 
            "Are you sure you want to restart the game? All progress will be lost.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reinitialize game
            self.game_controller.initialize_game()
            
            # Update UI
            self.update_game_ui()
    
    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self.db_manager, self.current_player, self)
        dialog.exec_()
        
        # Update game UI if settings have changed
        if self.game_controller:
            self.update_game_ui()
    
    def show_analytics(self):
        """Show the analytics dialog."""
        dialog = AnalyticsDialog(self.db_manager, self.current_player, self)
        dialog.exec_()
    
    def show_rules(self):
        """Show the game rules."""
        QMessageBox.information(
            self, "Game Rules", 
            "Scrabble Rules:\n\n"
            "1. Each player draws 7 tiles.\n"
            "2. The first player combines 2 or more tiles to form a word.\n"
            "3. Words can be placed horizontally or vertically.\n"
            "4. All subsequent words must connect with existing words.\n"
            "5. Score is calculated based on tile values and board bonuses.\n"
            "6. After each turn, draw new tiles to replace those used.\n"
            "7. Game ends when all tiles are used and one player has no tiles left,\n"
            "   or when no more plays are possible."
        )
    
    def show_about(self):
        """Show information about the application."""
        QMessageBox.about(
            self, "About Scrabble", 
            "Scrabble Game\nVersion 1.0\n\n"
            "A digital implementation of the classic word game Scrabble."
        )
    
    def show_move_result(self, success, message, score=0):
        """Show the result of a move."""
        if success:
            QMessageBox.information(
                self, "Move Successful", 
                f"{message}\nYou scored {score} points!"
            )
        else:
            QMessageBox.warning(
                self, "Invalid Move", message
            )
    
    def show_game_over(self, winner, player_score, ai_score):
        """Show game over dialog."""
        QMessageBox.information(
            self, "Game Over", 
            f"Game Over!\n\n"
            f"Winner: {winner}\n"
            f"Player Score: {player_score}\n"
            f"AI Score: {ai_score}"
        )
        
        # Ask if player wants to start a new game
        reply = QMessageBox.question(
            self, "New Game", 
            "Do you want to start a new game?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.new_game_dialog()
        else:
            self.stacked_widget.setCurrentIndex(0)  # Return to welcome screen
    
    def confirm_back_to_menu(self):
        """Confirm going back to the main menu."""
        if not self.game_controller:
            self.stacked_widget.setCurrentIndex(0)
            return
        
        reply = QMessageBox.question(
            self, "Return to Menu", 
            "Are you sure you want to return to the main menu? "
            "Unsaved progress will be lost.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Ask if player wants to save the game
            save_reply = QMessageBox.question(
                self, "Save Game", 
                "Do you want to save the current game?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )
            
            if save_reply == QMessageBox.Yes:
                self.save_game()
            
            self.stacked_widget.setCurrentIndex(0)
    
    def closeEvent(self, event):
        """Handle application close event."""
        if not self.game_controller or self.stacked_widget.currentIndex() == 0:
            event.accept()
            return
        
        reply = QMessageBox.question(
            self, "Exit Application", 
            "Are you sure you want to exit? Unsaved progress will be lost.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Ask if player wants to save the game
            save_reply = QMessageBox.question(
                self, "Save Game", 
                "Do you want to save the current game?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )
            
            if save_reply == QMessageBox.Yes:
                self.save_game()
            
            event.accept()
        else:
            event.ignore() 