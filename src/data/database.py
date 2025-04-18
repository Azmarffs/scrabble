#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from datetime import datetime

class DatabaseManager:
    """Manages SQLite database operations for the Scrabble game."""
    
    def __init__(self, db_path="resources/scrabble.db"):
        """Initialize database manager with path to database file."""
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def initialize_database(self):
        """Create database and tables if they don't exist."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Connect to database
        self.connect()
        
        # Create tables
        self._create_player_table()
        self._create_game_table()
        self._create_move_table()
        self._create_dictionary_table()
        self._create_settings_table()
        
        # Commit changes and close connection
        self.commit()
        self.close()
    
    def connect(self):
        """Connect to the SQLite database."""
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
    
    def commit(self):
        """Commit changes to the database."""
        if self.connection:
            self.connection.commit()
    
    def close(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        self.cursor = None
        self.connection = None
    
    def _create_player_table(self):
        """Create the player table if it doesn't exist."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            games_played INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            highest_score INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
    
    def _create_game_table(self):
        """Create the game table if it doesn't exist."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            ai_difficulty TEXT,
            player_score INTEGER DEFAULT 0,
            ai_score INTEGER DEFAULT 0,
            winner TEXT,
            duration INTEGER,
            date_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            board_config TEXT,
            completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
        ''')
    
    def _create_move_table(self):
        """Create the move table if it doesn't exist."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            player_id INTEGER,
            word TEXT,
            score INTEGER,
            position TEXT,
            direction TEXT,
            move_number INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games (id),
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
        ''')
    
    def _create_dictionary_table(self):
        """Create the dictionary table if it doesn't exist."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS dictionary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE,
            points INTEGER,
            theme TEXT
        )
        ''')
    
    def _create_settings_table(self):
        """Create the settings table if it doesn't exist."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            board_theme TEXT DEFAULT 'classic',
            tile_style TEXT DEFAULT 'default',
            ai_difficulty TEXT DEFAULT 'medium',
            sound_enabled BOOLEAN DEFAULT 1,
            animations_enabled BOOLEAN DEFAULT 1,
            hints_enabled BOOLEAN DEFAULT 1,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
        ''')
    
    def save_game(self, player_id, ai_difficulty, player_score, ai_score, 
                  winner, duration, board_config, completed=False):
        """Save a game to the database."""
        self.connect()
        self.cursor.execute('''
        INSERT INTO games (
            player_id, ai_difficulty, player_score, ai_score, winner, 
            duration, board_config, completed, date_played
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (player_id, ai_difficulty, player_score, ai_score, winner, 
              duration, board_config, completed, datetime.now()))
        
        game_id = self.cursor.lastrowid
        self.commit()
        self.close()
        return game_id
    
    def load_game(self, game_id):
        """Load a game from the database."""
        self.connect()
        self.cursor.execute('''
        SELECT * FROM games WHERE id = ?
        ''', (game_id,))
        game_data = self.cursor.fetchone()
        
        if game_data:
            # Get moves for this game
            self.cursor.execute('''
            SELECT * FROM moves WHERE game_id = ? ORDER BY move_number
            ''', (game_id,))
            moves = self.cursor.fetchall()
            
            self.close()
            return {
                'game': game_data,
                'moves': moves
            }
        
        self.close()
        return None
    
    def get_saved_games(self, player_id=None, completed=None):
        """Get list of saved games, optionally filtered by player and completion status."""
        self.connect()
        
        query = "SELECT * FROM games"
        params = []
        
        conditions = []
        if player_id is not None:
            conditions.append("player_id = ?")
            params.append(player_id)
        
        if completed is not None:
            conditions.append("completed = ?")
            params.append(1 if completed else 0)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY date_played DESC"
        
        self.cursor.execute(query, params)
        games = self.cursor.fetchall()
        self.close()
        
        return games
    
    def save_move(self, game_id, player_id, word, score, position, direction, move_number):
        """Save a move to the database."""
        self.connect()
        self.cursor.execute('''
        INSERT INTO moves (
            game_id, player_id, word, score, position, direction, move_number
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (game_id, player_id, word, score, position, direction, move_number))
        
        move_id = self.cursor.lastrowid
        self.commit()
        self.close()
        return move_id
    
    def get_player_stats(self, player_id):
        """Get statistics for a player."""
        self.connect()
        self.cursor.execute('''
        SELECT * FROM players WHERE id = ?
        ''', (player_id,))
        player = self.cursor.fetchone()
        
        if player:
            # Get additional stats
            self.cursor.execute('''
            SELECT 
                COUNT(*) as total_games,
                SUM(player_score) as total_score,
                MAX(player_score) as highest_score,
                COUNT(CASE WHEN winner = 'player' THEN 1 END) as wins,
                COUNT(CASE WHEN winner = 'ai' THEN 1 END) as losses
            FROM games
            WHERE player_id = ?
            ''', (player_id,))
            stats = self.cursor.fetchone()
            
            self.close()
            return {
                'player': player,
                'stats': stats
            }
        
        self.close()
        return None
    
    def add_dictionary_word(self, word, points, theme="standard"):
        """Add a word to the dictionary."""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT INTO dictionary (word, points, theme)
            VALUES (?, ?, ?)
            ''', (word.lower(), points, theme))
            self.commit()
            success = True
        except sqlite3.IntegrityError:
            # Word already exists
            success = False
        
        self.close()
        return success
    
    def is_valid_word(self, word, theme=None):
        """Check if a word exists in the dictionary."""
        self.connect()
        
        query = "SELECT 1 FROM dictionary WHERE word = ?"
        params = [word.lower()]
        
        if theme:
            query += " AND theme = ?"
            params.append(theme)
        
        self.cursor.execute(query, params)
        result = self.cursor.fetchone() is not None
        
        self.close()
        return result
    
    def get_word_points(self, word):
        """Get the base points value for a word."""
        self.connect()
        self.cursor.execute('''
        SELECT points FROM dictionary WHERE word = ?
        ''', (word.lower(),))
        result = self.cursor.fetchone()
        self.close()
        
        return result[0] if result else None
    
    def update_player_stats(self, player_id, games_played_inc=0, score_inc=0, highest_score=None):
        """Update a player's statistics."""
        self.connect()
        
        # Get current stats
        self.cursor.execute('''
        SELECT highest_score FROM players WHERE id = ?
        ''', (player_id,))
        current = self.cursor.fetchone()
        
        if not current:
            self.close()
            return False
        
        # Update highest score if necessary
        if highest_score is not None and highest_score > current[0]:
            self.cursor.execute('''
            UPDATE players
            SET games_played = games_played + ?,
                total_score = total_score + ?,
                highest_score = ?
            WHERE id = ?
            ''', (games_played_inc, score_inc, highest_score, player_id))
        else:
            self.cursor.execute('''
            UPDATE players
            SET games_played = games_played + ?,
                total_score = total_score + ?
            WHERE id = ?
            ''', (games_played_inc, score_inc, player_id))
        
        self.commit()
        self.close()
        return True
    
    def save_settings(self, player_id, settings):
        """Save player settings."""
        self.connect()
        
        # Check if settings exist for this player
        self.cursor.execute('''
        SELECT 1 FROM settings WHERE player_id = ?
        ''', (player_id,))
        exists = self.cursor.fetchone() is not None
        
        if exists:
            # Update existing settings
            query = "UPDATE settings SET "
            updates = []
            params = []
            
            for key, value in settings.items():
                updates.append(f"{key} = ?")
                params.append(value)
            
            query += ", ".join(updates)
            query += " WHERE player_id = ?"
            params.append(player_id)
            
            self.cursor.execute(query, params)
        else:
            # Insert new settings
            keys = ["player_id"] + list(settings.keys())
            placeholders = ["?"] * len(keys)
            values = [player_id] + list(settings.values())
            
            query = f"INSERT INTO settings ({', '.join(keys)}) VALUES ({', '.join(placeholders)})"
            self.cursor.execute(query, values)
        
        self.commit()
        self.close()
        return True
    
    def get_settings(self, player_id):
        """Get settings for a player."""
        self.connect()
        self.cursor.execute('''
        SELECT * FROM settings WHERE player_id = ?
        ''', (player_id,))
        settings = self.cursor.fetchone()
        self.close()
        
        return settings 