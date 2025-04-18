#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import time
from collections import deque

class AIPlayer:
    """AI player for Scrabble using Minimax with Alpha-Beta pruning."""
    
    def __init__(self, player, difficulty, board, word_validator, score_calculator):
        """Initialize the AI player.
        
        Args:
            player: The Player object for this AI.
            difficulty: The difficulty level ("easy", "medium", "hard").
            board: The game board.
            word_validator: The word validator.
            score_calculator: The score calculator.
        """
        self.player = player
        self.difficulty = difficulty.lower()
        self.board = board
        self.word_validator = word_validator
        self.score_calculator = score_calculator
        
        # Set depth for minimax based on difficulty
        if self.difficulty == "easy":
            self.minimax_depth = 1
            self.max_candidates = 3
        elif self.difficulty == "medium":
            self.minimax_depth = 2
            self.max_candidates = 5
        else:  # hard
            self.minimax_depth = 3
            self.max_candidates = 10
    
    def make_move(self, tiles_remaining):
        """Make a move based on the current board state and AI difficulty.
        
        Args:
            tiles_remaining: Number of tiles remaining in the bag.
            
        Returns:
            dict: A dictionary describing the move, or None if no move is possible.
        """
        # Get available moves
        candidate_moves = self.get_candidate_moves()
        
        if not candidate_moves:
            # No valid moves possible
            return None
        
        # Early game, mid game, or end game strategy
        if tiles_remaining > 70:  # Early game
            # Focus on building a strong position and scoring
            best_move = self.select_best_move(candidate_moves, prioritize_position=True)
        elif tiles_remaining > 20:  # Mid game
            # Balance between scoring and strategic positioning
            best_move = self.select_best_move(candidate_moves)
        else:  # End game
            # Maximize score and try to use all tiles
            best_move = self.select_best_move(candidate_moves, prioritize_score=True)
        
        return best_move
    
    def get_candidate_moves(self):
        """Generate candidate moves for the AI.
        
        Returns:
            list: A list of possible moves.
        """
        # Get the player's tiles
        tiles = self.player.get_tiles()
        
        # If this is the first move, place a word through the center
        if self.board.is_first_move():
            return self.get_first_move_candidates(tiles)
        
        # Find anchors (empty cells adjacent to existing tiles)
        anchors = self.find_anchors()
        
        # Generate candidate moves from each anchor point
        candidates = []
        
        for anchor in anchors:
            # Generate horizontal moves
            h_moves = self.generate_moves_from_anchor(anchor, "horizontal", tiles)
            candidates.extend(h_moves)
            
            # Generate vertical moves
            v_moves = self.generate_moves_from_anchor(anchor, "vertical", tiles)
            candidates.extend(v_moves)
        
        # Sort candidates by score in descending order
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Limit the number of candidates based on difficulty
        return candidates[:self.max_candidates]
    
    def get_first_move_candidates(self, tiles):
        """Generate candidate moves for the first move.
        
        Args:
            tiles: The player's tiles.
            
        Returns:
            list: A list of possible first moves.
        """
        candidates = []
        center_row, center_col = 7, 7  # Center of a standard 15x15 board
        
        # Generate all possible words from the player's tiles
        possible_words = self.generate_possible_words(tiles)
        
        for word in possible_words:
            # Try to place the word horizontally through the center
            for i in range(min(len(word), center_col + 1)):
                if i <= center_col and center_col - i + len(word) - 1 < 15:
                    start_col = center_col - i
                    
                    # Evaluate this placement
                    result = self.score_calculator.evaluate_word_placement(
                        word, (center_row, start_col), "horizontal", tiles, self.board
                    )
                    
                    if result['valid'] and self.validate_words(result['words']):
                        # Create a move dictionary
                        move = {
                            'word': word,
                            'position': (center_row, start_col),
                            'direction': 'horizontal',
                            'score': result['score'],
                            'tiles': []
                        }
                        
                        # Add the tiles used
                        row, col = center_row, start_col
                        for letter in word:
                            for tile_letter, tile_value in result['tiles_used']:
                                if tile_letter.upper() == letter.upper():
                                    move['tiles'].append((row, col, tile_letter, tile_value))
                                    break
                            col += 1
                        
                        candidates.append(move)
            
            # Try to place the word vertically through the center
            for i in range(min(len(word), center_row + 1)):
                if i <= center_row and center_row - i + len(word) - 1 < 15:
                    start_row = center_row - i
                    
                    # Evaluate this placement
                    result = self.score_calculator.evaluate_word_placement(
                        word, (start_row, center_col), "vertical", tiles, self.board
                    )
                    
                    if result['valid'] and self.validate_words(result['words']):
                        # Create a move dictionary
                        move = {
                            'word': word,
                            'position': (start_row, center_col),
                            'direction': 'vertical',
                            'score': result['score'],
                            'tiles': []
                        }
                        
                        # Add the tiles used
                        row, col = start_row, center_col
                        for letter in word:
                            for tile_letter, tile_value in result['tiles_used']:
                                if tile_letter.upper() == letter.upper():
                                    move['tiles'].append((row, col, tile_letter, tile_value))
                                    break
                            row += 1
                        
                        candidates.append(move)
        
        # Sort candidates by score in descending order
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return candidates[:self.max_candidates]
    
    def find_anchors(self):
        """Find anchor points (empty cells adjacent to existing tiles).
        
        Returns:
            list: A list of (row, col) tuples representing anchor points.
        """
        anchors = set()
        
        for row in range(self.board.size):
            for col in range(self.board.size):
                # If this cell has a tile, check adjacent cells
                if self.board.has_tile(row, col):
                    # Check adjacent cells (up, right, down, left)
                    for adj_row, adj_col in [(row - 1, col), (row, col + 1), 
                                            (row + 1, col), (row, col - 1)]:
                        if (0 <= adj_row < self.board.size and 
                            0 <= adj_col < self.board.size and 
                            not self.board.has_tile(adj_row, adj_col)):
                            anchors.add((adj_row, adj_col))
        
        return list(anchors)
    
    def generate_moves_from_anchor(self, anchor, direction, tiles):
        """Generate possible moves from an anchor point in a given direction.
        
        Args:
            anchor: The (row, col) anchor point.
            direction: "horizontal" or "vertical".
            tiles: The player's tiles.
            
        Returns:
            list: A list of possible moves.
        """
        row, col = anchor
        candidates = []
        
        # Generate all possible words from the player's tiles
        possible_words = self.generate_possible_words(tiles)
        
        for word in possible_words:
            # Try different starting positions for the word
            for i in range(len(word)):
                # Calculate the starting position
                if direction == "horizontal":
                    start_row, start_col = row, col - i
                else:  # vertical
                    start_row, start_col = row - i, col
                
                # Make sure the starting position is valid
                if (0 <= start_row < self.board.size and 
                    0 <= start_col < self.board.size):
                    
                    # Evaluate this placement
                    result = self.score_calculator.evaluate_word_placement(
                        word, (start_row, start_col), direction, tiles, self.board
                    )
                    
                    if result['valid'] and self.validate_words(result['words']):
                        # Create a move dictionary
                        move = {
                            'word': word,
                            'position': (start_row, start_col),
                            'direction': direction,
                            'score': result['score'],
                            'tiles': []
                        }
                        
                        # Add the tiles used
                        curr_row, curr_col = start_row, start_col
                        for letter in word:
                            found = False
                            
                            # If there's already a tile at this position, skip
                            if self.board.has_tile(curr_row, curr_col):
                                if direction == "horizontal":
                                    curr_col += 1
                                else:
                                    curr_row += 1
                                continue
                            
                            for tile_letter, tile_value in result['tiles_used']:
                                if tile_letter.upper() == letter.upper() and not found:
                                    move['tiles'].append((curr_row, curr_col, tile_letter, tile_value))
                                    found = True
                                    break
                            
                            if direction == "horizontal":
                                curr_col += 1
                            else:
                                curr_row += 1
                        
                        candidates.append(move)
        
        return candidates
    
    def generate_possible_words(self, tiles):
        """Generate possible words from the player's tiles.
        
        This is a simplified method that generates words directly instead of using a trie.
        For a real game, you would use a more efficient algorithm.
        
        Args:
            tiles: The player's tiles.
            
        Returns:
            list: A list of possible words.
        """
        # Letters available to the player
        available_letters = [letter.upper() for letter, _ in tiles]
        
        # Get all words from the dictionary (this is a simplification)
        self.word_validator.db_manager.connect()
        self.word_validator.db_manager.cursor.execute(
            "SELECT word FROM dictionary WHERE length(word) <= ? LIMIT 1000",
            (len(available_letters) + 5,)  # Allow for some existing tiles on the board
        )
        all_words = [row[0] for row in self.word_validator.db_manager.cursor.fetchall()]
        self.word_validator.db_manager.close()
        
        # Filter words that can be formed with the available letters
        possible_words = []
        
        for word in all_words:
            word = word.upper()
            if self.can_form_word(word, available_letters):
                possible_words.append(word)
        
        # Limit the number of words to prevent too much computation
        if len(possible_words) > 200:
            return random.sample(possible_words, 200)
        
        return possible_words
    
    def can_form_word(self, word, available_letters):
        """Check if a word can be formed with the available letters.
        
        This is a simplified check that doesn't account for letters already on the board.
        
        Args:
            word: The word to check.
            available_letters: The available letters.
            
        Returns:
            bool: True if the word can be formed, False otherwise.
        """
        # Make a copy of the available letters
        letters = available_letters.copy()
        
        for letter in word:
            if letter in letters:
                letters.remove(letter)
            else:
                return False
        
        return True
    
    def validate_words(self, words):
        """Validate that all words are in the dictionary.
        
        Args:
            words: A list of words to validate.
            
        Returns:
            bool: True if all words are valid, False otherwise.
        """
        for word in words:
            if not self.word_validator.is_valid_word(word):
                return False
        
        return True
    
    def select_best_move(self, candidate_moves, prioritize_score=False, prioritize_position=False):
        """Select the best move from candidate moves using Minimax.
        
        Args:
            candidate_moves: A list of candidate moves.
            prioritize_score: Whether to prioritize score over position.
            prioritize_position: Whether to prioritize position over score.
            
        Returns:
            dict: The best move, or None if no moves are available.
        """
        if not candidate_moves:
            return None
        
        # If only one move is available, return it
        if len(candidate_moves) == 1:
            return candidate_moves[0]
        
        # For easy difficulty or if prioritizing score, just return the highest scoring move
        if self.difficulty == "easy" or prioritize_score:
            return candidate_moves[0]
        
        # For medium difficulty, use a weighted random choice
        if self.difficulty == "medium":
            # Calculate weights based on score
            total_score = sum(move['score'] for move in candidate_moves)
            if total_score == 0:
                # If all moves have zero score, use equal weights
                weights = [1 / len(candidate_moves)] * len(candidate_moves)
            else:
                weights = [move['score'] / total_score for move in candidate_moves]
            
            # Make a weighted random choice
            return random.choices(candidate_moves, weights=weights, k=1)[0]
        
        # For hard difficulty, use minimax with alpha-beta pruning
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        for move in candidate_moves[:min(len(candidate_moves), self.max_candidates)]:
            # Apply the move
            self.apply_move(move)
            
            # Evaluate with minimax
            score = self.minimax(self.minimax_depth - 1, False, alpha, beta)
            
            # Undo the move
            self.undo_move(move)
            
            # Update best move if this one is better
            if score > best_score:
                best_score = score
                best_move = move
            
            # Update alpha
            alpha = max(alpha, best_score)
            
            # Alpha-beta pruning
            if beta <= alpha:
                break
        
        return best_move or candidate_moves[0]
    
    def minimax(self, depth, is_maximizing, alpha, beta):
        """Minimax algorithm with alpha-beta pruning.
        
        Args:
            depth: The current depth.
            is_maximizing: Whether it's the maximizing player's turn.
            alpha: The alpha value for pruning.
            beta: The beta value for pruning.
            
        Returns:
            float: The evaluated score.
        """
        if depth == 0:
            return self.evaluate_board()
        
        if is_maximizing:
            max_eval = float('-inf')
            
            # Generate moves for AI
            candidate_moves = self.get_candidate_moves()
            
            for move in candidate_moves[:min(len(candidate_moves), 3)]:  # Limit to 3 moves for efficiency
                self.apply_move(move)
                eval_score = self.minimax(depth - 1, False, alpha, beta)
                self.undo_move(move)
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break
            
            return max_eval
        else:
            min_eval = float('inf')
            
            # Simulate opponent moves (simplified)
            # In a real implementation, you'd generate actual opponent moves
            opponent_moves = [{'score': 5}, {'score': 10}, {'score': 15}]
            
            for move in opponent_moves:
                # Simulate opponent move (simplified)
                eval_score = self.minimax(depth - 1, True, alpha, beta) - move['score']
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break
            
            return min_eval
    
    def evaluate_board(self):
        """Evaluate the current board state.
        
        Returns:
            float: The evaluation score.
        """
        # This is a simplified evaluation function
        # In a real implementation, you'd consider more factors
        
        # Count the number of tiles placed by the AI
        ai_tiles_count = 0
        for row in range(self.board.size):
            for col in range(self.board.size):
                if self.board.has_tile(row, col):
                    ai_tiles_count += 1
        
        # Consider the remaining tiles in the AI's rack
        rack_potential = sum(value for _, value in self.player.get_tiles())
        
        # Evaluate board control (simplified)
        control_score = 0
        for row in range(self.board.size):
            for col in range(self.board.size):
                if self.board.has_tile(row, col):
                    # Add points for controlling premium squares
                    bonus_type = self.board.get_bonus_type(row, col)
                    if bonus_type == self.board.DOUBLE_WORD or bonus_type == self.board.TRIPLE_WORD:
                        control_score += 3
                    elif bonus_type == self.board.DOUBLE_LETTER or bonus_type == self.board.TRIPLE_LETTER:
                        control_score += 1
        
        return ai_tiles_count * 2 + rack_potential + control_score
    
    def apply_move(self, move):
        """Apply a move to the board (for simulation).
        
        Args:
            move: The move to apply.
        """
        # Place tiles on the board
        for row, col, letter, value in move['tiles']:
            self.board.place_tile(row, col, letter, value)
            
            # Remove from player's rack
            for i, (rack_letter, rack_value) in enumerate(self.player.tiles):
                if rack_letter.upper() == letter.upper():
                    self.player.tiles.pop(i)
                    break
    
    def undo_move(self, move):
        """Undo a move from the board (for simulation).
        
        Args:
            move: The move to undo.
        """
        # Remove tiles from the board and add back to rack
        for row, col, letter, value in move['tiles']:
            self.board.remove_tile(row, col)
            
            # Add back to player's rack
            self.player.tiles.append((letter, value))