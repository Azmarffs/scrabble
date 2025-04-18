#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Board:
    """Represents the Scrabble game board."""
    
    # Bonus tile types
    NORMAL = 0
    DOUBLE_LETTER = 1
    TRIPLE_LETTER = 2
    DOUBLE_WORD = 3
    TRIPLE_WORD = 4
    
    def __init__(self, size=15):
        """Initialize a new board with the specified size.
        
        Args:
            size: The size of the board (default is 15x15 for standard Scrabble).
        """
        self.size = size
        
        # Initialize the board grid
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        
        # Initialize the bonus grid
        self.bonus_grid = [[self.NORMAL for _ in range(size)] for _ in range(size)]
        self.initialize_bonus_tiles()
    
    def initialize_bonus_tiles(self):
        """Initialize the bonus tiles on the board with standard Scrabble layout."""
        # Triple word score
        for row, col in [(0, 0), (0, 7), (0, 14),
                          (7, 0), (7, 14),
                          (14, 0), (14, 7), (14, 14)]:
            self.bonus_grid[row][col] = self.TRIPLE_WORD
        
        # Double word score
        for row, col in [(1, 1), (2, 2), (3, 3), (4, 4),
                          (1, 13), (2, 12), (3, 11), (4, 10),
                          (10, 4), (11, 3), (12, 2), (13, 1),
                          (10, 10), (11, 11), (12, 12), (13, 13)]:
            self.bonus_grid[row][col] = self.DOUBLE_WORD
        
        # Triple letter score
        for row, col in [(1, 5), (1, 9),
                          (5, 1), (5, 5), (5, 9), (5, 13),
                          (9, 1), (9, 5), (9, 9), (9, 13),
                          (13, 5), (13, 9)]:
            self.bonus_grid[row][col] = self.TRIPLE_LETTER
        
        # Double letter score
        for row, col in [(0, 3), (0, 11),
                          (2, 6), (2, 8),
                          (3, 0), (3, 7), (3, 14),
                          (6, 2), (6, 6), (6, 8), (6, 12),
                          (7, 3), (7, 11),
                          (8, 2), (8, 6), (8, 8), (8, 12),
                          (11, 0), (11, 7), (11, 14),
                          (12, 6), (12, 8),
                          (14, 3), (14, 11)]:
            self.bonus_grid[row][col] = self.DOUBLE_LETTER
    
    def place_tile(self, row, col, letter, value):
        """Place a tile on the board at the specified position.
        
        Args:
            row: The row index (0-based).
            col: The column index (0-based).
            letter: The letter on the tile.
            value: The point value of the tile.
            
        Returns:
            bool: True if the tile was placed, False if the position is invalid or occupied.
        """
        # Check if the position is valid
        if not self.is_valid_position(row, col):
            return False
        
        # Check if the position is already occupied
        if self.grid[row][col] is not None:
            return False
        
        # Place the tile
        self.grid[row][col] = (letter.upper(), value)
        return True
    
    def remove_tile(self, row, col):
        """Remove a tile from the board at the specified position.
        
        Args:
            row: The row index (0-based).
            col: The column index (0-based).
            
        Returns:
            bool: True if a tile was removed, False if the position is invalid or empty.
        """
        # Check if the position is valid
        if not self.is_valid_position(row, col):
            return False
        
        # Check if there's a tile to remove
        if self.grid[row][col] is None:
            return False
        
        # Remove the tile
        self.grid[row][col] = None
        return True
    
    def get_tile(self, row, col):
        """Get the tile at the specified position.
        
        Args:
            row: The row index (0-based).
            col: The column index (0-based).
            
        Returns:
            tuple: A (letter, value) tuple, or None if the position is empty or invalid.
        """
        if not self.is_valid_position(row, col):
            return None
        
        return self.grid[row][col]
    
    def has_tile(self, row, col):
        """Check if there's a tile at the specified position.
        
        Args:
            row: The row index (0-based).
            col: The column index (0-based).
            
        Returns:
            bool: True if there's a tile, False otherwise.
        """
        if not self.is_valid_position(row, col):
            return False
        
        return self.grid[row][col] is not None
    
    def get_bonus_type(self, row, col):
        """Get the bonus type at the specified position.
        
        Args:
            row: The row index (0-based).
            col: The column index (0-based).
            
        Returns:
            int: The bonus type, or None if the position is invalid.
        """
        if not self.is_valid_position(row, col):
            return None
        
        return self.bonus_grid[row][col]
    
    def is_valid_position(self, row, col):
        """Check if the specified position is valid on the board.
        
        Args:
            row: The row index (0-based).
            col: The column index (0-based).
            
        Returns:
            bool: True if the position is valid, False otherwise.
        """
        return 0 <= row < self.size and 0 <= col < self.size
    
    def is_first_move(self):
        """Check if this is the first move (i.e., the board is empty).
        
        Returns:
            bool: True if the board is empty, False otherwise.
        """
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] is not None:
                    return False
        return True
    
    def get_words_from_move(self, tiles):
        """Get all words formed by placing the given tiles on the board.
        
        Args:
            tiles: A list of (row, col, letter, value) tuples representing the tiles to place.
            
        Returns:
            list: A list of (word, positions) tuples, where positions is a list of (row, col) tuples.
        """
        # Temporarily place the tiles on the board
        original_grid = [row[:] for row in self.grid]
        
        for row, col, letter, value in tiles:
            self.grid[row][col] = (letter.upper(), value)
        
        words = []
        
        # Check if the move is horizontal, vertical, or a single tile
        if len(tiles) <= 1:
            # Single tile, check both directions
            for row, col, _, _ in tiles:
                h_word = self.get_word_at(row, col, True)
                v_word = self.get_word_at(row, col, False)
                
                if h_word and len(h_word[0]) > 1:
                    words.append(h_word)
                
                if v_word and len(v_word[0]) > 1:
                    words.append(v_word)
        else:
            # Check if the move is horizontal
            is_horizontal = all(tiles[0][0] == tile[0] for tile in tiles)
            
            # Get the main word
            for row, col, _, _ in tiles:
                word = self.get_word_at(row, col, is_horizontal)
                if word and len(word[0]) > 1 and word not in words:
                    words.append(word)
                
                # Get perpendicular words
                perp_word = self.get_word_at(row, col, not is_horizontal)
                if perp_word and len(perp_word[0]) > 1 and perp_word not in words:
                    words.append(perp_word)
        
        # Restore the original grid
        self.grid = original_grid
        
        return words
    
    def get_word_at(self, row, col, horizontal=True):
        """Get the word at the specified position in the given direction.
        
        Args:
            row: The row index (0-based).
            col: The column index (0-based).
            horizontal: True for horizontal, False for vertical.
            
        Returns:
            tuple: A (word, positions) tuple, or None if no word is found.
                  positions is a list of (row, col) tuples.
        """
        if not self.has_tile(row, col):
            return None
        
        # Find the start of the word
        start_row, start_col = row, col
        
        if horizontal:
            while start_col > 0 and self.has_tile(start_row, start_col - 1):
                start_col -= 1
        else:
            while start_row > 0 and self.has_tile(start_row - 1, start_col):
                start_row -= 1
        
        # Collect the word and positions
        word = ""
        positions = []
        curr_row, curr_col = start_row, start_col
        
        while self.is_valid_position(curr_row, curr_col) and self.has_tile(curr_row, curr_col):
            letter, _ = self.grid[curr_row][curr_col]
            word += letter
            positions.append((curr_row, curr_col))
            
            if horizontal:
                curr_col += 1
            else:
                curr_row += 1
        
        return (word, positions) if word else None
    
    def randomize_bonus_tiles(self):
        """Randomize the positions of bonus tiles while maintaining the same distribution."""
        import random
        
        # Count current bonus types
        bonus_counts = {
            self.DOUBLE_LETTER: 0,
            self.TRIPLE_LETTER: 0,
            self.DOUBLE_WORD: 0,
            self.TRIPLE_WORD: 0
        }
        
        for row in range(self.size):
            for col in range(self.size):
                bonus_type = self.bonus_grid[row][col]
                if bonus_type != self.NORMAL:
                    bonus_counts[bonus_type] += 1
        
        # Reset all bonus tiles to normal
        self.bonus_grid = [[self.NORMAL for _ in range(self.size)] for _ in range(self.size)]
        
        # Set the center tile to double word
        center = self.size // 2
        self.bonus_grid[center][center] = self.DOUBLE_WORD
        bonus_counts[self.DOUBLE_WORD] -= 1
        
        # Keep track of assigned positions
        assigned_positions = {(center, center)}
        
        # Randomly distribute the remaining bonus tiles
        for bonus_type, count in bonus_counts.items():
            for _ in range(count):
                while True:
                    row = random.randint(0, self.size - 1)
                    col = random.randint(0, self.size - 1)
                    
                    if (row, col) not in assigned_positions:
                        self.bonus_grid[row][col] = bonus_type
                        assigned_positions.add((row, col))
                        break 