#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.game.board import Board

class ScoreCalculator:
    """Calculates scores for words in Scrabble."""
    
    def __init__(self):
        """Initialize the score calculator."""
        pass
    
    def calculate_score(self, word, positions, board):
        """Calculate the score for a word.
        
        Args:
            word: The word to calculate the score for.
            positions: A list of (row, col) tuples indicating tile positions.
            board: The game board.
            
        Returns:
            int: The calculated score.
        """
        if not word or not positions:
            return 0
        
        # Get each letter's base value and apply letter bonuses
        letter_scores = []
        word_multiplier = 1
        
        for i, (row, col) in enumerate(positions):
            # Get the letter and its value
            tile = board.get_tile(row, col)
            if not tile:  # This shouldn't happen with valid positions
                continue
            
            letter, value = tile
            
            # Apply letter bonus if applicable
            bonus_type = board.get_bonus_type(row, col)
            
            if bonus_type == Board.DOUBLE_LETTER:
                letter_scores.append(value * 2)
            elif bonus_type == Board.TRIPLE_LETTER:
                letter_scores.append(value * 3)
            else:
                letter_scores.append(value)
            
            # Accumulate word multipliers
            if bonus_type == Board.DOUBLE_WORD:
                word_multiplier *= 2
            elif bonus_type == Board.TRIPLE_WORD:
                word_multiplier *= 3
        
        # Calculate base score
        base_score = sum(letter_scores)
        
        # Apply word multiplier
        final_score = base_score * word_multiplier
        
        # Add bingo bonus if all 7 tiles were used
        if len(positions) == 7:  # Standard Scrabble gives 50 bonus points for using all 7 tiles
            final_score += 50
        
        return final_score
    
    def calculate_move_score(self, words_and_positions, board):
        """Calculate the total score for a move (which might create multiple words).
        
        Args:
            words_and_positions: A list of (word, positions) tuples.
            board: The game board.
            
        Returns:
            int: The total score for the move.
        """
        total_score = 0
        
        for word, positions in words_and_positions:
            word_score = self.calculate_score(word, positions, board)
            total_score += word_score
        
        return total_score
    
    def evaluate_word_placement(self, word, position, direction, player_tiles, board):
        """Evaluate the potential score for placing a word at a position.
        
        This is used by the AI to evaluate possible moves.
        
        Args:
            word: The word to place.
            position: The (row, col) starting position.
            direction: "horizontal" or "vertical".
            player_tiles: A list of (letter, value) tuples representing the player's tiles.
            board: The game board.
            
        Returns:
            dict: A dictionary with keys:
                - 'score': The potential score.
                - 'valid': Whether the placement is valid.
                - 'words': A list of words formed.
                - 'tiles_used': A list of tiles used from the player's rack.
        """
        # Make a copy of the current board state
        original_grid = [row[:] for row in board.grid]
        
        # Check if the player has the necessary tiles
        available_letters = [letter.upper() for letter, _ in player_tiles]
        tiles_used = []
        
        start_row, start_col = position
        current_row, current_col = start_row, start_col
        
        # Try to place the word on the board
        for letter in word.upper():
            # Check if the position is out of bounds
            if not board.is_valid_position(current_row, current_col):
                # Restore the board
                board.grid = original_grid
                return {'score': 0, 'valid': False, 'words': [], 'tiles_used': []}
            
            # If there's already a tile at this position, it must match the letter
            if board.has_tile(current_row, current_col):
                existing_letter, _ = board.get_tile(current_row, current_col)
                if existing_letter.upper() != letter:
                    # Restore the board
                    board.grid = original_grid
                    return {'score': 0, 'valid': False, 'words': [], 'tiles_used': []}
            else:
                # We need to use a tile from the player's rack
                if letter in available_letters:
                    available_letters.remove(letter)
                    
                    # Find the value of this letter
                    for rack_letter, value in player_tiles:
                        if rack_letter.upper() == letter and (rack_letter.upper(), value) not in tiles_used:
                            tiles_used.append((rack_letter.upper(), value))
                            # Place the tile
                            board.place_tile(current_row, current_col, letter, value)
                            break
                else:
                    # Player doesn't have the required tile
                    # Restore the board
                    board.grid = original_grid
                    return {'score': 0, 'valid': False, 'words': [], 'tiles_used': []}
            
            # Move to the next position
            if direction == "horizontal":
                current_col += 1
            else:
                current_row += 1
        
        # At this point, the word has been successfully placed
        # Get all words formed by the placement
        tile_positions = []
        
        current_row, current_col = start_row, start_col
        for _ in word:
            if board.has_tile(current_row, current_col):
                tile_positions.append((current_row, current_col))
                
                if direction == "horizontal":
                    current_col += 1
                else:
                    current_row += 1
        
        words_formed = board.get_words_from_move(
            [(row, col, board.get_tile(row, col)[0], board.get_tile(row, col)[1]) 
             for row, col in tile_positions]
        )
        
        # Calculate the score for all words formed
        total_score = self.calculate_move_score(words_formed, board)
        
        # Restore the board
        board.grid = original_grid
        
        return {
            'score': total_score,
            'valid': True,
            'words': [word for word, _ in words_formed],
            'tiles_used': tiles_used
        } 