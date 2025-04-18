#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLabel, QComboBox, QCheckBox, QPushButton,
                           QGroupBox, QRadioButton, QButtonGroup, QTabWidget, QWidget)
from PyQt5.QtCore import Qt, QSettings

class SettingsDialog(QDialog):
    """Dialog for configuring game settings."""
    
    def __init__(self, db_manager, player, parent=None):
        """Initialize the settings dialog.
        
        Args:
            db_manager: The database manager.
            player: The current player (or None if no game is in progress).
            parent: The parent widget.
        """
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.player = player
        self.settings = QSettings()
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Game Settings tab
        game_tab = QWidget()
        game_layout = QVBoxLayout(game_tab)
        
        # AI Difficulty
        difficulty_group = QGroupBox("AI Difficulty")
        difficulty_layout = QVBoxLayout()
        
        self.easy_radio = QRadioButton("Easy")
        self.medium_radio = QRadioButton("Medium")
        self.hard_radio = QRadioButton("Hard")
        
        difficulty_layout.addWidget(self.easy_radio)
        difficulty_layout.addWidget(self.medium_radio)
        difficulty_layout.addWidget(self.hard_radio)
        
        difficulty_group.setLayout(difficulty_layout)
        game_layout.addWidget(difficulty_group)
        
        # Word themes
        theme_group = QGroupBox("Word Theme")
        theme_layout = QVBoxLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Standard", "Science", "Technology", "Nature", "Custom"])
        
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        game_layout.addWidget(theme_group)
        
        # Game rules
        rules_group = QGroupBox("Game Rules")
        rules_layout = QVBoxLayout()
        
        self.hints_check = QCheckBox("Enable Hints")
        self.strict_mode_check = QCheckBox("Strict Mode (Challenges allowed)")
        self.timer_check = QCheckBox("Use Timer (60 seconds per turn)")
        
        rules_layout.addWidget(self.hints_check)
        rules_layout.addWidget(self.strict_mode_check)
        rules_layout.addWidget(self.timer_check)
        
        rules_group.setLayout(rules_layout)
        game_layout.addWidget(rules_group)
        
        # Add game tab to tab widget
        tab_widget.addTab(game_tab, "Game")
        
        # Display Settings tab
        display_tab = QWidget()
        display_layout = QVBoxLayout(display_tab)
        
        # Board theme
        board_group = QGroupBox("Board Theme")
        board_layout = QVBoxLayout()
        
        self.board_theme_combo = QComboBox()
        self.board_theme_combo.addItems(["Classic", "Modern", "Dark", "Light", "Wooden"])
        
        board_layout.addWidget(self.board_theme_combo)
        board_group.setLayout(board_layout)
        display_layout.addWidget(board_group)
        
        # Tile style
        tile_group = QGroupBox("Tile Style")
        tile_layout = QVBoxLayout()
        
        self.tile_style_combo = QComboBox()
        self.tile_style_combo.addItems(["Classic", "Modern", "Dark", "Light", "Wooden"])
        
        tile_layout.addWidget(self.tile_style_combo)
        tile_group.setLayout(tile_layout)
        display_layout.addWidget(tile_group)
        
        # Visual options
        visual_group = QGroupBox("Visual Options")
        visual_layout = QVBoxLayout()
        
        self.animations_check = QCheckBox("Enable Animations")
        self.highlight_check = QCheckBox("Highlight Valid Words")
        self.show_score_check = QCheckBox("Show Potential Score")
        
        visual_layout.addWidget(self.animations_check)
        visual_layout.addWidget(self.highlight_check)
        visual_layout.addWidget(self.show_score_check)
        
        visual_group.setLayout(visual_layout)
        display_layout.addWidget(visual_group)
        
        # Add display tab to tab widget
        tab_widget.addTab(display_tab, "Display")
        
        # Sound Settings tab
        sound_tab = QWidget()
        sound_layout = QVBoxLayout(sound_tab)
        
        # Sound options
        sound_group = QGroupBox("Sound Options")
        sound_layout_group = QVBoxLayout()
        
        self.sound_check = QCheckBox("Enable Sound")
        self.music_check = QCheckBox("Enable Background Music")
        self.effects_check = QCheckBox("Enable Sound Effects")
        
        sound_layout_group.addWidget(self.sound_check)
        sound_layout_group.addWidget(self.music_check)
        sound_layout_group.addWidget(self.effects_check)
        
        sound_group.setLayout(sound_layout_group)
        sound_layout.addWidget(sound_group)
        
        # Volume
        volume_group = QGroupBox("Volume")
        volume_layout = QFormLayout()
        
        self.master_volume_combo = QComboBox()
        self.master_volume_combo.addItems(["Mute", "Low", "Medium", "High"])
        
        self.music_volume_combo = QComboBox()
        self.music_volume_combo.addItems(["Mute", "Low", "Medium", "High"])
        
        self.effects_volume_combo = QComboBox()
        self.effects_volume_combo.addItems(["Mute", "Low", "Medium", "High"])
        
        volume_layout.addRow("Master Volume:", self.master_volume_combo)
        volume_layout.addRow("Music Volume:", self.music_volume_combo)
        volume_layout.addRow("Effects Volume:", self.effects_volume_combo)
        
        volume_group.setLayout(volume_layout)
        sound_layout.addWidget(volume_group)
        
        # Add sound tab to tab widget
        tab_widget.addTab(sound_tab, "Sound")
        
        # Add tab widget to main layout
        main_layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setDefault(True)
        
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(button_layout)
        
        # Group radio buttons
        self.difficulty_group = QButtonGroup(self)
        self.difficulty_group.addButton(self.easy_radio, 0)
        self.difficulty_group.addButton(self.medium_radio, 1)
        self.difficulty_group.addButton(self.hard_radio, 2)
        
        # Connect signals
        self.sound_check.toggled.connect(self.toggle_sound_options)
    
    def load_settings(self):
        """Load settings from QSettings and database."""
        # Load difficulty
        difficulty = self.settings.value("ai_difficulty", "medium").lower()
        if difficulty == "easy":
            self.easy_radio.setChecked(True)
        elif difficulty == "medium":
            self.medium_radio.setChecked(True)
        else:
            self.hard_radio.setChecked(True)
        
        # Load word theme
        theme = self.settings.value("word_theme", "Standard")
        index = self.theme_combo.findText(theme, Qt.MatchFixedString)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Load game rules
        self.hints_check.setChecked(self.settings.value("hints_enabled", True, type=bool))
        self.strict_mode_check.setChecked(self.settings.value("strict_mode", False, type=bool))
        self.timer_check.setChecked(self.settings.value("use_timer", False, type=bool))
        
        # Load board theme
        board_theme = self.settings.value("board_theme", "Classic")
        index = self.board_theme_combo.findText(board_theme, Qt.MatchFixedString)
        if index >= 0:
            self.board_theme_combo.setCurrentIndex(index)
        
        # Load tile style
        tile_style = self.settings.value("tile_style", "Classic")
        index = self.tile_style_combo.findText(tile_style, Qt.MatchFixedString)
        if index >= 0:
            self.tile_style_combo.setCurrentIndex(index)
        
        # Load visual options
        self.animations_check.setChecked(self.settings.value("animations_enabled", True, type=bool))
        self.highlight_check.setChecked(self.settings.value("highlight_valid_words", True, type=bool))
        self.show_score_check.setChecked(self.settings.value("show_potential_score", True, type=bool))
        
        # Load sound options
        self.sound_check.setChecked(self.settings.value("sound_enabled", True, type=bool))
        self.music_check.setChecked(self.settings.value("music_enabled", True, type=bool))
        self.effects_check.setChecked(self.settings.value("effects_enabled", True, type=bool))
        
        # Load volume settings
        master_volume = self.settings.value("master_volume", "Medium")
        index = self.master_volume_combo.findText(master_volume, Qt.MatchFixedString)
        if index >= 0:
            self.master_volume_combo.setCurrentIndex(index)
        
        music_volume = self.settings.value("music_volume", "Medium")
        index = self.music_volume_combo.findText(music_volume, Qt.MatchFixedString)
        if index >= 0:
            self.music_volume_combo.setCurrentIndex(index)
        
        effects_volume = self.settings.value("effects_volume", "Medium")
        index = self.effects_volume_combo.findText(effects_volume, Qt.MatchFixedString)
        if index >= 0:
            self.effects_volume_combo.setCurrentIndex(index)
        
        # Update state of sound options based on master sound setting
        self.toggle_sound_options(self.sound_check.isChecked())
        
        # Load additional settings from database if player exists
        if self.player:
            settings = self.db_manager.get_settings(self.player.id)
            if settings:
                # Database settings would override defaults if they exist
                pass
    
    def save_settings(self):
        """Save settings to QSettings and database."""
        # Save difficulty
        if self.easy_radio.isChecked():
            self.settings.setValue("ai_difficulty", "easy")
        elif self.medium_radio.isChecked():
            self.settings.setValue("ai_difficulty", "medium")
        else:
            self.settings.setValue("ai_difficulty", "hard")
        
        # Save word theme
        self.settings.setValue("word_theme", self.theme_combo.currentText())
        
        # Save game rules
        self.settings.setValue("hints_enabled", self.hints_check.isChecked())
        self.settings.setValue("strict_mode", self.strict_mode_check.isChecked())
        self.settings.setValue("use_timer", self.timer_check.isChecked())
        
        # Save board theme
        self.settings.setValue("board_theme", self.board_theme_combo.currentText())
        
        # Save tile style
        self.settings.setValue("tile_style", self.tile_style_combo.currentText())
        
        # Save visual options
        self.settings.setValue("animations_enabled", self.animations_check.isChecked())
        self.settings.setValue("highlight_valid_words", self.highlight_check.isChecked())
        self.settings.setValue("show_potential_score", self.show_score_check.isChecked())
        
        # Save sound options
        self.settings.setValue("sound_enabled", self.sound_check.isChecked())
        self.settings.setValue("music_enabled", self.music_check.isChecked())
        self.settings.setValue("effects_enabled", self.effects_check.isChecked())
        
        # Save volume settings
        self.settings.setValue("master_volume", self.master_volume_combo.currentText())
        self.settings.setValue("music_volume", self.music_volume_combo.currentText())
        self.settings.setValue("effects_volume", self.effects_volume_combo.currentText())
        
        # Save to database if player exists
        if self.player:
            # Create a settings dictionary
            settings_dict = {
                'board_theme': self.board_theme_combo.currentText().lower(),
                'tile_style': self.tile_style_combo.currentText().lower(),
                'ai_difficulty': self.get_difficulty(),
                'sound_enabled': 1 if self.sound_check.isChecked() else 0,
                'animations_enabled': 1 if self.animations_check.isChecked() else 0,
                'hints_enabled': 1 if self.hints_check.isChecked() else 0
            }
            
            # Save to database
            self.db_manager.save_settings(self.player.id, settings_dict)
        
        # Accept dialog
        self.accept()
    
    def get_difficulty(self):
        """Get the selected difficulty level.
        
        Returns:
            str: The difficulty level ("easy", "medium", or "hard").
        """
        if self.easy_radio.isChecked():
            return "easy"
        elif self.medium_radio.isChecked():
            return "medium"
        else:
            return "hard"
    
    def reset_to_defaults(self):
        """Reset all settings to their default values."""
        # Game settings
        self.medium_radio.setChecked(True)
        self.theme_combo.setCurrentIndex(0)  # Standard
        self.hints_check.setChecked(True)
        self.strict_mode_check.setChecked(False)
        self.timer_check.setChecked(False)
        
        # Display settings
        self.board_theme_combo.setCurrentIndex(0)  # Classic
        self.tile_style_combo.setCurrentIndex(0)  # Classic
        self.animations_check.setChecked(True)
        self.highlight_check.setChecked(True)
        self.show_score_check.setChecked(True)
        
        # Sound settings
        self.sound_check.setChecked(True)
        self.music_check.setChecked(True)
        self.effects_check.setChecked(True)
        self.master_volume_combo.setCurrentIndex(2)  # Medium
        self.music_volume_combo.setCurrentIndex(2)  # Medium
        self.effects_volume_combo.setCurrentIndex(2)  # Medium
        
        # Update dependent UI elements
        self.toggle_sound_options(True)
    
    def toggle_sound_options(self, enabled):
        """Enable or disable sound options based on master sound setting.
        
        Args:
            enabled: Whether sound is enabled.
        """
        self.music_check.setEnabled(enabled)
        self.effects_check.setEnabled(enabled)
        self.master_volume_combo.setEnabled(enabled)
        self.music_volume_combo.setEnabled(enabled and self.music_check.isChecked())
        self.effects_volume_combo.setEnabled(enabled and self.effects_check.isChecked()) 