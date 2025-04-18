#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Player:
    """Represents a player in the Scrabble game."""
    
    def __init__(self, player_id, name, is_ai=False):
        """Initialize a new player.
        
        Args:
            player_id: The player's ID in the database.
            name: The player's name.
            is_ai: Whether the player is an AI opponent.
        """
        self.id = player_id
        self.name = name
        self.is_ai = is_ai
        self.tiles = []  # List of (letter, value) tuples
    
    def add_tile(self, letter, value):
        """Add a tile to the player's rack.
        
        Args:
            letter: The letter on the tile.
            value: The point value of the tile.
            
        Returns:
            bool: True if the tile was added, False if the rack is full.
        """
        if len(self.tiles) < 7:  # Standard Scrabble rack size is 7
            self.tiles.append((letter.upper(), value))
            return True
        return False
    
    def remove_tile(self, letter):
        """Remove a tile with the given letter from the player's rack.
        
        Args:
            letter: The letter to remove.
            
        Returns:
            bool: True if the tile was removed, False if not found.
        """
        letter = letter.upper()
        for i, (tile_letter, tile_value) in enumerate(self.tiles):
            if tile_letter == letter:
                self.tiles.pop(i)
                return True
        return False
    
    def has_tile(self, letter):
        """Check if the player has a tile with the given letter.
        
        Args:
            letter: The letter to check for.
            
        Returns:
            bool: True if the player has the tile, False otherwise.
        """
        letter = letter.upper()
        return any(tile_letter == letter for tile_letter, _ in self.tiles)
    
    def get_tile_value(self, letter):
        """Get the value of a tile with the given letter.
        
        Args:
            letter: The letter to check for.
            
        Returns:
            int: The value of the tile, or None if not found.
        """
        letter = letter.upper()
        for tile_letter, tile_value in self.tiles:
            if tile_letter == letter:
                return tile_value
        return None
    
    def set_tiles(self, tiles):
        """Set the player's tiles.
        
        Args:
            tiles: A list of (letter, value) tuples.
        """
        self.tiles = [(letter.upper(), value) for letter, value in tiles]
    
    def get_tiles(self):
        """Get the player's tiles.
        
        Returns:
            list: A list of (letter, value) tuples.
        """
        return self.tiles
    
    def get_tile_count(self):
        """Get the number of tiles in the player's rack.
        
        Returns:
            int: The number of tiles.
        """
        return len(self.tiles)
    
    def has_tiles(self, letters):
        """Check if the player has all the specified letters.
        
        Args:
            letters: A list of letters to check for.
            
        Returns:
            bool: True if the player has all the letters, False otherwise.
        """
        rack_letters = [letter for letter, _ in self.tiles]
        
        # Convert letters to a list if it's a string
        if isinstance(letters, str):
            letters = list(letters)
        
        # Make a copy of the rack letters to avoid modifying the original
        available_letters = rack_letters.copy()
        
        for letter in letters:
            letter = letter.upper()
            if letter in available_letters:
                available_letters.remove(letter)
            else:
                return False
        
        return True 