#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import random
from PyQt5.QtCore import QTimer
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from src.game.board import Board
from src.game.tile_bag import TileBag
from src.game.player import Player
from src.game.word_validator import WordValidator
from src.game.score_calculator import ScoreCalculator
from src.ai.ai_player import AIPlayer

class GameController(QObject):
    """Controls the game logic and state."""
    
    # Signals
    board_updated = pyqtSignal(list)  # List of board updates
    rack_updated = pyqtSignal(list)  # List of (letter, value) pairs
    game_info_updated = pyqtSignal(dict)  # Dictionary of game info
    move_result = pyqtSignal(bool, str, int)  # Success, message, score
    game_over = pyqtSignal(str, int, int)  # Winner, player score, AI score
    
    def __init__(self, db_manager, player, difficulty="medium"):
        """Initialize game controller with database manager and player."""
        super().__init__()
        
        self.db_manager = db_manager
        self.player = player
        self.difficulty = difficulty.lower()
        
        # Game components
        self.board = None
        self.tile_bag = None
        self.word_validator = None
        self.score_calculator = None
        self.ai_player = None
        
        # Game state
        self.current_player = None  # "player" or "ai"
        self.game_id = None
        self.start_time = None
        self.game_time = "00:00"
        self.turn_number = 1
        self.is_game_over = False
        self.current_move_tiles = []  # [(row, col, letter, value), ...]
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game_time)
        self.challenge_timer = QTimer()
        self.challenge_timer.timeout.connect(self.challenge_timeout)
        self.challenge_time = 30  # 30 seconds to make a challenge
        self.challenge_remaining = 0
        self.can_challenge = False
        self.current_challenge = None
        self.challenge_penalty = 10  # Points deducted for failed challenge
        # Statistics
        self.player_score = 0
        self.ai_score = 0
        self.pass_count = 0  # Consecutive passes
        self.last_move = {"player": "None", "word": "None", "score": 0}
    
    def initialize_game(self):
        """Initialize a new game."""
        # Initialize game components
        self.board = Board()
        self.tile_bag = TileBag()
        self.word_validator = WordValidator(self.db_manager)
        self.score_calculator = ScoreCalculator()
        
        # Create AI player
        ai_player = Player(-1, "AI", is_ai=True)
        self.ai_player = AIPlayer(ai_player, self.difficulty, self.board, 
                                  self.word_validator, self.score_calculator)
        
        # Draw initial tiles for players
        self.player.set_tiles(self.tile_bag.draw_tiles(7))
        self.ai_player.player.set_tiles(self.tile_bag.draw_tiles(7))
        
        # Set initial game state
        self.current_player = "player"  # Player goes first
        self.start_time = datetime.now()
        self.turn_number = 1
        self.is_game_over = False
        self.player_score = 0
        self.ai_score = 0
        self.pass_count = 0
        self.current_move_tiles = []
        
        # Start game timer
        self.timer.start(1000)  # Update every second
        
        # Emit signals to update UI
        self.emit_board_update()
        self.emit_rack_update()
        self.emit_game_info_update()
    
    def start_challenge_period(self):
        """Start the period during which a word can be challenged."""
        self.can_challenge = True
        self.challenge_remaining = self.challenge_time
        self.challenge_timer.start(1000)  # Update every second
        self.emit_game_info_update()

    def challenge_timeout(self):
        """Handle challenge timer timeout."""
        self.challenge_remaining -= 1
        if self.challenge_remaining <= 0:
            self.end_challenge_period()
        self.emit_game_info_update()

    def end_challenge_period(self):
        """End the challenge period."""
        self.challenge_timer.stop()
        self.can_challenge = False
        self.challenge_remaining = 0
        self.emit_game_info_update()

    def challenge_word(self, word):
        """Challenge the validity of a word.
        
        Args:
            word: The word being challenged.
            
        Returns:
            bool: True if challenge successful, False if failed.
        """
        if not self.can_challenge:
            return False

        # Check if word is actually valid
        is_valid = self.word_validator.is_valid_word(word)
        
        if not is_valid:
            # Challenge successful - remove word and deduct points
            self.handle_successful_challenge(word)
            return True
        else:
            # Challenge failed - penalize challenger
            self.handle_failed_challenge()
            return False

    def handle_successful_challenge(self, word):
        """Handle a successful word challenge.
        
        Args:
            word: The successfully challenged word.
        """
        # Find the move that placed this word
        for row, col, letter, value in self.current_move_tiles:
            self.board.remove_tile(row, col)
            self.ai_player.player.add_tile(letter, value)

        # Deduct points from AI's score
        self.ai_score -= self.last_move["score"]
        
        # Update game state
        self.end_challenge_period()
        self.emit_board_update()
        self.emit_game_info_update()

    def handle_failed_challenge(self):
        """Handle a failed word challenge."""
        # Deduct penalty points from player
        self.player_score = max(0, self.player_score - self.challenge_penalty)
        
        # End challenge period
        self.end_challenge_period()
        self.emit_game_info_update()
    
    def load_game(self, game_data):
        """Load a saved game."""
        # Extract game data
        game = game_data['game']
        moves = game_data['moves']
        
        # Initialize components
        self.board = Board()
        self.tile_bag = TileBag()
        self.word_validator = WordValidator(self.db_manager)
        self.score_calculator = ScoreCalculator()
        
        # Create AI player
        ai_player = Player(-1, "AI", is_ai=True)
        self.ai_player = AIPlayer(ai_player, game[2], self.board, 
                                 self.word_validator, self.score_calculator)
        
        # Load board configuration
        board_config = json.loads(game[8])  # board_config is at index 8
        for pos, tile_info in board_config.items():
            row, col = map(int, pos.strip('()').split(','))
            letter, value = tile_info
            self.board.place_tile(row, col, letter, value)
        
        # Set game state from saved data
        self.game_id = game[0]  # id is at index 0
        self.player_score = game[3]  # player_score is at index 3
        self.ai_score = game[4]  # ai_score is at index 4
        
        # Set player tiles (from saved state or draw new ones)
        # For simplicity, we'll draw new tiles for now
        tiles_on_board_count = len(board_config)
        tiles_used = tiles_on_board_count + 14  # 7 tiles per player
        for _ in range(tiles_used):
            self.tile_bag.draw_tiles(1)  # Discard to match the state
        
        self.player.set_tiles(self.tile_bag.draw_tiles(7))
        self.ai_player.player.set_tiles(self.tile_bag.draw_tiles(7))
        
        # Set current player (simplification: always start with player's turn when loading)
        self.current_player = "player"
        
        # Set other game state
        self.start_time = datetime.now() - timedelta(seconds=game[6] or 0)  # duration is at index 6
        self.turn_number = len(moves) + 1
        self.is_game_over = bool(game[9])  # completed is at index 9
        self.pass_count = 0
        self.current_move_tiles = []
        
        # Start game timer
        self.timer.start(1000)
        
        # Emit signals to update UI
        self.emit_board_update()
        self.emit_rack_update()
        self.emit_game_info_update()
    
    def update_game_time(self):
        """Update the game time."""
        if self.start_time and not self.is_game_over:
            delta = datetime.now() - self.start_time
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if hours > 0:
                self.game_time = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                self.game_time = f"{minutes:02}:{seconds:02}"
            
            self.emit_game_info_update()
    
    def place_tile(self, row, col, letter, value):
        """Place a tile on the board."""
        if self.current_player != "player" or self.is_game_over:
            return False
        
        # Place tile on board
        if self.board.place_tile(row, col, letter, value):
            # Add to current move
            self.current_move_tiles.append((row, col, letter, value))
            
            # Remove from player's rack
            self.player.remove_tile(letter)
            
            # Emit signals
            self.emit_board_update()
            self.emit_rack_update()
            
            return True
        
        return False
    
    def remove_tile(self, row, col):
        """Remove a tile from the board."""
        if self.current_player != "player" or self.is_game_over:
            return False
        
        # Check if the tile is part of the current move
        for i, (tile_row, tile_col, letter, value) in enumerate(self.current_move_tiles):
            if tile_row == row and tile_col == col:
                # Remove from current move
                tile_data = self.current_move_tiles.pop(i)
                
                # Add back to player's rack
                self.player.add_tile(tile_data[2], tile_data[3])
                
                # Remove from board
                self.board.remove_tile(row, col)
                
                # Emit signals
                self.emit_board_update()
                self.emit_rack_update()
                
                return True
        
        return False
    
    def select_tile(self, letter, value):
        """Select a tile from the player's rack."""
        # This is just a pass-through to track the selected tile
        # The actual selection is handled by the UI
        return True
    
    def submit_move(self):
        """Submit the current move."""
        if self.current_player != "player" or self.is_game_over:
            return False
        
        # Check if any tiles have been placed
        if not self.current_move_tiles:
            self.move_result.emit(False, "No tiles placed.", 0)
            return False
        
        # Validate the move
        words, is_valid, message = self.validate_move()
        
        if not is_valid:
            # Revert the move
            self.recall_tiles()
            self.move_result.emit(False, message, 0)
            return False
        
        # Calculate score
        score = 0
        main_word = ""
        
        for word, word_positions in words:
            word_score = self.score_calculator.calculate_score(word, word_positions, self.board)
            score += word_score
            
            # The main word is the one with the most tiles from the current move
            if len(word) > len(main_word):
                main_word = word
        
        # Update player score
        self.player_score += score
        
        # Save move to database
        if self.game_id:
            # Convert positions to string for database
            pos_str = ','.join([f"({r},{c})" for r, c, _, _ in self.current_move_tiles])
            direction = "horizontal" if self.is_horizontal_move() else "vertical"
            
            self.db_manager.save_move(
                self.game_id, 
                self.player.id, 
                main_word, 
                score, 
                pos_str, 
                direction, 
                self.turn_number
            )
        
        # Update last move info
        self.last_move = {
            "player": "player",
            "word": main_word,
            "score": score
        }
        
        # Reset current move
        self.current_move_tiles = []
        
        # Draw new tiles
        new_tiles = self.tile_bag.draw_tiles(7 - len(self.player.tiles))
        for letter, value in new_tiles:
            self.player.add_tile(letter, value)
        
        # Reset pass count
        self.pass_count = 0
        
        # Update UI
        self.emit_rack_update()
        self.emit_game_info_update()
        
        # Emit move result
        self.move_result.emit(True, f"Valid move! Word: {main_word}", score)
        
        # Check for game over
        if self.check_game_over():
            return True
        
        # Switch to AI's turn
        self.current_player = "ai"
        self.emit_game_info_update()
        
        # Let AI make a move (with a slight delay for UX)
        QTimer.singleShot(1000, self.ai_move)
        
        return True
    
    def validate_move(self):
        """Validate the current move."""
        # Check if this is the first move
        is_first_move = self.board.is_first_move()
        
        # Check if tiles are placed in a line
        if not self.is_tiles_in_line():
            return [], False, "Tiles must be placed in a line."
        
        # Check if tiles are connected to existing tiles (except first move)
        if not is_first_move and not self.is_connected_to_existing():
            return [], False, "Tiles must be connected to existing tiles."
        
        # Check if first move covers the center cell
        if is_first_move and not self.covers_center():
            return [], False, "First move must cover the center cell."
        
        # Check if the words formed are valid
        words = self.board.get_words_from_move(self.current_move_tiles)
        
        invalid_words = []
        for word, _ in words:
            if not self.word_validator.is_valid_word(word):
                invalid_words.append(word)
        
        if invalid_words:
            word_list = ", ".join(invalid_words)
            return [], False, f"Invalid word(s): {word_list}"
        
        return words, True, "Valid move."
    
    def is_tiles_in_line(self):
        """Check if the placed tiles are in a line."""
        if len(self.current_move_tiles) <= 1:
            return True
        
        # Check if all tiles are in the same row
        same_row = all(t[0] == self.current_move_tiles[0][0] for t in self.current_move_tiles)
        
        # Check if all tiles are in the same column
        same_col = all(t[1] == self.current_move_tiles[0][1] for t in self.current_move_tiles)
        
        return same_row or same_col
    
    def is_horizontal_move(self):
        """Check if the current move is horizontal."""
        if len(self.current_move_tiles) <= 1:
            return True  # Default to horizontal for single tile
        
        # If all tiles have the same row, it's horizontal
        return all(t[0] == self.current_move_tiles[0][0] for t in self.current_move_tiles)
    
    def is_connected_to_existing(self):
        """Check if the placed tiles are connected to existing tiles."""
        # Get positions of current move tiles
        current_positions = set((r, c) for r, c, _, _ in self.current_move_tiles)
        
        # Check if any placed tile is adjacent to an existing tile
        for row, col, _, _ in self.current_move_tiles:
            # Check adjacent cells (up, right, down, left)
            adjacent_positions = [
                (row - 1, col), 
                (row, col + 1), 
                (row + 1, col), 
                (row, col - 1)
            ]
            
            for adj_row, adj_col in adjacent_positions:
                # Skip if out of bounds
                if not (0 <= adj_row < 15 and 0 <= adj_col < 15):
                    continue
                
                # Skip if it's part of the current move
                if (adj_row, adj_col) in current_positions:
                    continue
                
                # If there's a tile at this position, it's connected
                if self.board.has_tile(adj_row, adj_col):
                    return True
        
        return False
    
    def covers_center(self):
        """Check if the move covers the center cell."""
        center_row, center_col = 7, 7
        
        for row, col, _, _ in self.current_move_tiles:
            if row == center_row and col == center_col:
                return True
        
        return False
    
    def recall_tiles(self):
        """Recall all tiles from the current move back to the rack."""
        if self.current_player != "player" or self.is_game_over:
            return False
        
        # Remove tiles from board and add back to rack
        for row, col, letter, value in self.current_move_tiles:
            self.board.remove_tile(row, col)
            self.player.add_tile(letter, value)
        
        # Clear current move
        self.current_move_tiles = []
        
        # Emit signals
        self.emit_board_update()
        self.emit_rack_update()
        
        return True
    
    def pass_turn(self):
        """Pass the current turn."""
        if self.current_player != "player" or self.is_game_over:
            return False
        
        # Recall any tiles placed but not submitted
        if self.current_move_tiles:
            self.recall_tiles()
        
        # Increment pass count
        self.pass_count += 1
        
        # Update last move info
        self.last_move = {
            "player": "player",
            "word": "PASS",
            "score": 0
        }
        
        # Check for game over (3 consecutive passes)
        if self.pass_count >= 6:  # 3 rounds of passes (player and AI)
            self.end_game()
            return True
        
        # Switch to AI's turn
        self.current_player = "ai"
        self.emit_game_info_update()
        
        # Let AI make a move
        QTimer.singleShot(1000, self.ai_move)
        
        return True
    
    def ai_move(self):
        """Execute the AI's move."""
        if self.current_player != "ai" or self.is_game_over:
            return

        # Get AI move
        move = self.ai_player.make_move(self.tile_bag.get_remaining_tiles_count())

        if move and move['tiles']:
            # Place tiles on board
            for row, col, letter, value in move['tiles']:
                self.board.place_tile(row, col, letter, value)
                self.ai_player.player.remove_tile(letter)

            # Update score
            self.ai_score += move['score']

            # Update last move info
            self.last_move = {
                "player": "ai",
                "word": move['word'],
                "score": move['score']
            }

            # Start challenge period
            self.start_challenge_period()

            # Reset pass count
            self.pass_count = 0

            # Draw new tiles for AI
            new_tiles = self.tile_bag.draw_tiles(7 - len(self.ai_player.player.tiles))
            for letter, value in new_tiles:
                self.ai_player.player.add_tile(letter, value)
        else:
            # AI passes
            self.pass_count += 1

            # Update last move info
            self.last_move = {
                "player": "ai",
                "word": "PASS",
                "score": 0
            }

        # Save move to database if a game is in progress
        if self.game_id and move and move['tiles']:
            # Convert positions to string for database
            pos_str = ','.join([f"({r},{c})" for r, c, _, _ in move['tiles']])
            direction = "horizontal" if move['direction'] == 'horizontal' else "vertical"

            self.db_manager.save_move(
                self.game_id,
                -1,  # AI player ID
                move['word'],
                move['score'],
                pos_str,
                direction,
                self.turn_number
            )

        # Increment turn number
        self.turn_number += 1

        # Check for game over
        if self.check_game_over():
            return

        # Switch back to player's turn
        self.current_player = "player"

        # Emit signals
        self.emit_board_update()
        self.emit_game_info_update()
    
    def check_game_over(self):
        """Check if the game is over."""
        # Check if bag is empty and either player has no tiles
        if (self.tile_bag.is_empty() and 
            (len(self.player.tiles) == 0 or len(self.ai_player.player.tiles) == 0)):
            self.end_game()
            return True
        
        # Check if 6 consecutive passes (3 full rounds)
        if self.pass_count >= 6:
            self.end_game()
            return True
        
        return False
    
    def end_game(self):
        """End the game and calculate final scores."""
        self.is_game_over = True
        self.timer.stop()
        
        # Calculate remaining tile values
        player_remaining = sum(value for _, value in self.player.tiles)
        ai_remaining = sum(value for _, value in self.ai_player.player.tiles)
        
        # Adjust scores based on remaining tiles
        if len(self.player.tiles) == 0:
            self.player_score += ai_remaining
            self.ai_score -= ai_remaining
        elif len(self.ai_player.player.tiles) == 0:
            self.ai_score += player_remaining
            self.player_score -= player_remaining
        # If game ended due to passes, subtract remaining tile values
        else:
            self.player_score -= player_remaining
            self.ai_score -= ai_remaining
        
        # Determine winner
        if self.player_score > self.ai_score:
            winner = "Player"
        elif self.ai_score > self.player_score:
            winner = "AI"
        else:
            winner = "Tie"
        
        # Update game in database if it exists
        if self.game_id:
            # Calculate duration
            duration = int((datetime.now() - self.start_time).total_seconds())
            
            # Get board state as JSON
            board_state = {}
            for row in range(15):
                for col in range(15):
                    if self.board.has_tile(row, col):
                        letter, value = self.board.get_tile(row, col)
                        board_state[f"({row},{col})"] = [letter, value]
            
            board_config = json.dumps(board_state)
            
            # Update game in database
            self.db_manager.connect()
            self.db_manager.cursor.execute("""
            UPDATE games 
            SET player_score = ?, ai_score = ?, winner = ?, 
                duration = ?, board_config = ?, completed = 1
            WHERE id = ?
            """, (
                self.player_score, 
                self.ai_score, 
                winner.lower(), 
                duration, 
                board_config, 
                self.game_id
            ))
            self.db_manager.commit()
            self.db_manager.close()
            
            # Update player stats
            self.db_manager.update_player_stats(
                self.player.id,
                games_played_inc=1,
                score_inc=self.player_score,
                highest_score=self.player_score
            )
        
        # Emit signals
        self.emit_game_info_update()
        self.game_over.emit(winner, self.player_score, self.ai_score)
    
    def save_game(self):
        """Save the current game state to the database."""
        if self.is_game_over:
            return self.game_id
        
        # Calculate duration
        duration = int((datetime.now() - self.start_time).total_seconds())
        
        # Get board state as JSON
        board_state = {}
        for row in range(15):
            for col in range(15):
                if self.board.has_tile(row, col):
                    letter, value = self.board.get_tile(row, col)
                    board_state[f"({row},{col})"] = [letter, value]
        
        board_config = json.dumps(board_state)
        
        # Determine current leader as temporary winner
        winner = "player" if self.player_score > self.ai_score else "ai"
        if self.player_score == self.ai_score:
            winner = "tie"
        
        # If we already have a game ID, update it
        if self.game_id:
            self.db_manager.connect()
            self.db_manager.cursor.execute("""
            UPDATE games 
            SET player_score = ?, ai_score = ?, winner = ?, 
                duration = ?, board_config = ?
            WHERE id = ?
            """, (
                self.player_score, 
                self.ai_score, 
                winner, 
                duration, 
                board_config, 
                self.game_id
            ))
            self.db_manager.commit()
            self.db_manager.close()
        else:
            # Create a new game record
            self.game_id = self.db_manager.save_game(
                self.player.id,
                self.difficulty,
                self.player_score,
                self.ai_score,
                winner,
                duration,
                board_config
            )
        
        return self.game_id
    
    def pause_game(self):
        """Pause the game."""
        self.timer.stop()
    
    def resume_game(self):
        """Resume the game."""
        if not self.is_game_over:
            self.timer.start(1000)
    
    def get_board_state(self):
        """Get the current state of the board."""
        board_state = {}
        for row in range(15):
            for col in range(15):
                if self.board.has_tile(row, col):
                    letter, value = self.board.get_tile(row, col)
                    board_state[(row, col)] = (letter, value)
        return board_state
    
    def get_player_tiles(self):
        """Get the current tiles in the player's rack."""
        return self.player.get_tiles()
    
    def get_game_info(self):
        """Get the current game information."""
        info = {
            'player_score': self.player_score,
            'ai_score': self.ai_score,
            'difficulty': self.difficulty,
            'is_player_turn': self.current_player == "player",
            'turn_number': self.turn_number,
            'tiles_remaining': self.tile_bag.get_remaining_tiles_count(),
            'progress': min(100, int(((100 - self.tile_bag.get_remaining_tiles_count()) / 100) * 100)),
            'game_time': self.game_time,
            'last_move': self.last_move,
            'can_challenge': self.can_challenge,
            'challenge_time': self.challenge_remaining
        }
        return info
    
    def emit_board_update(self):
        """Emit a signal to update the board."""
        # For now, we'll just emit the full board state
        # In a more optimized version, we could only emit the changes
        updates = []
        for row in range(15):
            for col in range(15):
                if self.board.has_tile(row, col):
                    letter, value = self.board.get_tile(row, col)
                    updates.append((row, col, 'place', letter, value))
        
        self.board_updated.emit(updates)
    
    def emit_rack_update(self):
        """Emit a signal to update the player's rack."""
        self.rack_updated.emit(self.player.get_tiles())
    
    def emit_game_info_update(self):
        """Emit a signal to update the game information."""
        self.game_info_updated.emit(self.get_game_info()) 