#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import nltk

class WordValidator:
    """Validates words against a Scrabble dictionary."""
    
    def __init__(self, db_manager, theme=None):
        """Initialize the word validator.
        
        Args:
            db_manager: The database manager.
            theme: Optional theme filter for words.
        """
        self.db_manager = db_manager
        self.theme = theme
        
        # Initialize the dictionary from the database
        self.initialize_dictionary()
    
    def initialize_dictionary(self):
        """Initialize the dictionary from various sources."""
        # Check if we need to load the initial dictionary
        self.db_manager.connect()
        self.db_manager.cursor.execute("SELECT COUNT(*) FROM dictionary")
        count = self.db_manager.cursor.fetchone()[0]
        self.db_manager.close()
        
        if count == 0:
            self.load_nltk_dictionary()
    
    def load_nltk_dictionary(self):
        """Load words from NLTK corpus."""
        try:
            # Download NLTK word lists if not already available
            nltk.download('words', quiet=True)
            nltk.download('scowl-wl', quiet=True)
            
            # Get words from NLTK corpus
            from nltk.corpus import words as nltk_words
            
            word_list = set(word.lower() for word in nltk_words.words())
            
            # Filter words: Scrabble rules typically allow 2-15 letter words
            valid_words = [word for word in word_list if 2 <= len(word) <= 15]
            
            # Add words to the database
            self.db_manager.connect()
            
            for word in valid_words:
                # Calculate basic point value (just sum of letter values)
                points = self.calculate_base_points(word)
                self.db_manager.cursor.execute(
                    "INSERT OR IGNORE INTO dictionary (word, points, theme) VALUES (?, ?, ?)",
                    (word.lower(), points, "standard")
                )
            
            self.db_manager.commit()
            self.db_manager.close()
            
        except Exception as e:
            print(f"Error loading NLTK dictionary: {e}")
    
    def calculate_base_points(self, word):
        """Calculate the base point value for a word (without board bonuses).
        
        Args:
            word: The word to calculate points for.
            
        Returns:
            int: The base point value.
        """
        # Standard Scrabble letter values
        letter_values = {
            'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1,
            'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1,
            'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10
        }
        
        return sum(letter_values.get(letter.upper(), 0) for letter in word)
    
    def is_valid_word(self, word, theme=None):
        """Check if a word exists in the dictionary.
        
        Args:
            word: The word to check.
            theme: Optional theme to check against (defaults to the validator's theme).
            
        Returns:
            bool: True if the word is valid, False otherwise.
        """
        # Use the specified theme or fall back to the validator's theme
        current_theme = theme or self.theme
        
        # Check if the word is in the dictionary
        return self.db_manager.is_valid_word(word, current_theme)
    
    def get_word_value(self, word):
        """Get the base value of a word.
        
        Args:
            word: The word to get the value for.
            
        Returns:
            int: The base point value, or None if the word is not in the dictionary.
        """
        return self.db_manager.get_word_points(word)
    
    def add_word(self, word, theme="standard"):
        """Add a word to the dictionary.
        
        Args:
            word: The word to add.
            theme: The theme to assign to the word.
            
        Returns:
            bool: True if the word was added, False if it already exists.
        """
        # Calculate base points
        points = self.calculate_base_points(word)
        
        # Add to the database
        return self.db_manager.add_dictionary_word(word, points, theme)
    
    def get_word_themes(self, word):
        """Get all themes a word belongs to.
        
        Args:
            word: The word to check.
            
        Returns:
            list: A list of themes.
        """
        self.db_manager.connect()
        self.db_manager.cursor.execute(
            "SELECT theme FROM dictionary WHERE word = ?",
            (word.lower(),)
        )
        themes = [row[0] for row in self.db_manager.cursor.fetchall()]
        self.db_manager.close()
        
        return themes
    
    def load_theme_dictionary(self, theme, file_path):
        """Load a themed dictionary from a file.
        
        Args:
            theme: The theme to assign to the words.
            file_path: Path to a file containing words, one per line.
            
        Returns:
            int: The number of words added.
        """
        if not os.path.exists(file_path):
            return 0
        
        added_count = 0
        
        try:
            with open(file_path, 'r') as f:
                words = [line.strip().lower() for line in f if line.strip()]
            
            self.db_manager.connect()
            
            for word in words:
                if 2 <= len(word) <= 15:  # Valid Scrabble word length
                    points = self.calculate_base_points(word)
                    try:
                        self.db_manager.cursor.execute(
                            "INSERT INTO dictionary (word, points, theme) VALUES (?, ?, ?)",
                            (word, points, theme)
                        )
                        added_count += 1
                    except sqlite3.IntegrityError:
                        # Word with this theme already exists
                        pass
            
            self.db_manager.commit()
            self.db_manager.close()
            
        except Exception as e:
            print(f"Error loading theme dictionary: {e}")
        
        return added_count
    
    def set_theme(self, theme):
        """Set the theme filter for the validator.
        
        Args:
            theme: The theme to filter by, or None for no filter.
        """
        self.theme = theme 