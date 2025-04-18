#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random

class TileBag:
    """Represents the bag of letter tiles in a Scrabble game."""
    
    # Standard Scrabble tile distribution and values
    TILE_DISTRIBUTION = {
        'A': {'count': 9, 'value': 1},
        'B': {'count': 2, 'value': 3},
        'C': {'count': 2, 'value': 3},
        'D': {'count': 4, 'value': 2},
        'E': {'count': 12, 'value': 1},
        'F': {'count': 2, 'value': 4},
        'G': {'count': 3, 'value': 2},
        'H': {'count': 2, 'value': 4},
        'I': {'count': 9, 'value': 1},
        'J': {'count': 1, 'value': 8},
        'K': {'count': 1, 'value': 5},
        'L': {'count': 4, 'value': 1},
        'M': {'count': 2, 'value': 3},
        'N': {'count': 6, 'value': 1},
        'O': {'count': 8, 'value': 1},
        'P': {'count': 2, 'value': 3},
        'Q': {'count': 1, 'value': 10},
        'R': {'count': 6, 'value': 1},
        'S': {'count': 4, 'value': 1},
        'T': {'count': 6, 'value': 1},
        'U': {'count': 4, 'value': 1},
        'V': {'count': 2, 'value': 4},
        'W': {'count': 2, 'value': 4},
        'X': {'count': 1, 'value': 8},
        'Y': {'count': 2, 'value': 4},
        'Z': {'count': 1, 'value': 10},
        ' ': {'count': 2, 'value': 0}  # blank tiles
    }
    
    def __init__(self, custom_distribution=None):
        """Initialize a new tile bag.
        
        Args:
            custom_distribution: Optional custom tile distribution.
        """
        self.tiles = []
        self.distribution = custom_distribution or self.TILE_DISTRIBUTION
        self.initialize_tiles()
    
    def initialize_tiles(self):
        """Initialize the bag with tiles according to the distribution."""
        self.tiles = []
        
        for letter, info in self.distribution.items():
            for _ in range(info['count']):
                self.tiles.append((letter, info['value']))
        
        # Shuffle the tiles
        random.shuffle(self.tiles)
    
    def draw_tiles(self, count):
        """Draw a specified number of tiles from the bag.
        
        Args:
            count: The number of tiles to draw.
            
        Returns:
            list: A list of (letter, value) tuples.
        """
        # Make sure we don't try to draw more tiles than available
        count = min(count, len(self.tiles))
        
        # Draw the tiles
        drawn_tiles = []
        for _ in range(count):
            if self.tiles:  # Check if there are tiles left
                drawn_tiles.append(self.tiles.pop())
        
        return drawn_tiles
    
    def return_tiles(self, tiles):
        """Return tiles to the bag and shuffle.
        
        Args:
            tiles: A list of (letter, value) tuples to return to the bag.
        """
        self.tiles.extend(tiles)
        random.shuffle(self.tiles)
    
    def exchange_tiles(self, tiles_to_exchange):
        """Exchange tiles with the bag.
        
        Args:
            tiles_to_exchange: A list of (letter, value) tuples to exchange.
            
        Returns:
            list: A list of new (letter, value) tuples.
        """
        # Make sure the bag has enough tiles for the exchange
        if len(tiles_to_exchange) > len(self.tiles):
            return []
        
        # Draw new tiles
        new_tiles = self.draw_tiles(len(tiles_to_exchange))
        
        # Return the exchanged tiles to the bag
        self.return_tiles(tiles_to_exchange)
        
        return new_tiles
    
    def get_remaining_tiles_count(self):
        """Get the number of tiles remaining in the bag.
        
        Returns:
            int: The number of tiles remaining.
        """
        return len(self.tiles)
    
    def get_remaining_tiles(self):
        """Get a list of all remaining tiles (for AI calculations).
        
        Returns:
            list: A list of (letter, value) tuples.
        """
        return self.tiles.copy()
    
    def is_empty(self):
        """Check if the bag is empty.
        
        Returns:
            bool: True if the bag is empty, False otherwise.
        """
        return len(self.tiles) == 0
    
    def get_letter_count(self, letter):
        """Get the number of tiles of a specific letter remaining in the bag.
        
        Args:
            letter: The letter to count.
            
        Returns:
            int: The number of tiles of the specified letter.
        """
        letter = letter.upper()
        return sum(1 for tile_letter, _ in self.tiles if tile_letter == letter)
    
    def get_letter_value(self, letter):
        """Get the point value of a specific letter.
        
        Args:
            letter: The letter to get the value for.
            
        Returns:
            int: The point value of the letter.
        """
        letter = letter.upper()
        if letter in self.distribution:
            return self.distribution[letter]['value']
        return 0 