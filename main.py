import pygame
import sys
import time
import logging
import random
from constants import WIDTH, HEIGHT, FPS, BLACK
from board import ChessBoard
from utils import load_piece_images
from powerups import PowerUpType
from pieces import Color, PieceType, Piece

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChessRoguelike")

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Roguelike")
    clock = pygame.time.Clock()
    
    # Load piece images
    piece_images = load_piece_images()
    
    # Create chess board
    chess_board = ChessBoard()
    
    # Create Stockfish AI
    ai = None
    ai_enabled = False
    ai_error_message = None
    
    try:
        # Import here to avoid errors if Stockfish isn't installed
        from chess_ai import ChessAI
        
        # Initialize Stockfish AI with difficulty level 3 (range is 1-10)
        ai = ChessAI(difficulty=3, max_time=0.5)
        ai_enabled = True
        ai_move_delay = 0.2  # Delay in seconds before making the AI move
        last_ai_move_time = 0
        logger.info("Stockfish AI initialized successfully!")
    except Exception as e:
        ai_error_message = f"AI Error: {str(e)}"
        logger.error(f"Failed to initialize Stockfish AI: {e}")
        logger.error("Make sure Stockfish is installed and in your PATH or game directory.")
    
    # Create font for UI elements
    font = pygame.font.SysFont("Arial", 16)
    
    running = True
    while running:
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and ai is not None:
                    # Toggle AI on/off with 'A' key
                    ai_enabled = not ai_enabled
                    logger.info(f"AI: {'enabled' if ai_enabled else 'disabled'}")
                elif event.key == pygame.K_r:
                    # Reset the game with 'R' key
                    chess_board = ChessBoard()
                    logger.info("Game reset")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Only allow player to move white pieces
                    if chess_board.current_turn == Color.WHITE:
                        chess_board.handle_click(event.pos)
                        
                        # Check if a move was made
                        if chess_board.current_turn == Color.BLACK:
                            # A move was made, clear error messages
                            ai_error_message = None
        
        # AI move if it's Black's turn
        if (ai_enabled and ai is not None and 
            chess_board.current_turn == Color.BLACK and 
            not chess_board.powerup_system.show_powerup_selection and
            current_time - last_ai_move_time >= ai_move_delay):
            
            try:
                logger.info("AI is thinking...")
                
                # Get the best move from Stockfish
                piece, target_pos = ai.get_best_move(chess_board)
                
                logger.info(f"AI suggests moving {piece.piece_type.name} from {piece.position} to {target_pos}")
                
                # Validate the move
                valid_moves = chess_board.get_valid_moves(piece)
                logger.info(f"Valid moves for {piece.piece_type.name}: {valid_moves}")
                
                if target_pos in valid_moves:
                    # DIRECT APPROACH: Instead of relying on move_piece, manually update the board
                    logger.info(f"Making move: {piece.piece_type.name} to {target_pos}")
                    
                    # Get the current position
                    row, col = piece.position
                    target_row, target_col = target_pos
                    
                    # Clear the old position
                    chess_board.board[row][col] = None
                    
                    # Move to the new position
                    piece.position = target_pos
                    piece.has_moved = True
                    chess_board.board[target_row][target_col] = piece
                    
                    # Switch turns
                    chess_board.current_turn = Color.WHITE
                    
                    # Update visualization
                    chess_board.selected_piece = None
                    chess_board.valid_moves = []
                    
                    # Provide detailed logging to confirm the move
                    logger.info(f"Piece moved. New board state: Black {piece.piece_type.name} now at {target_pos}")
                else:
                    logger.error(f"Invalid move suggested: {target_pos} not in {valid_moves}")
                    # Try a random valid move as fallback
                    if valid_moves:
                        random_move = random.choice(valid_moves)
                        logger.info(f"Using random move instead: {random_move}")
                        
                        # Same direct approach for the random move
                        row, col = piece.position
                        target_row, target_col = random_move
                        
                        chess_board.board[row][col] = None
                        piece.position = random_move
                        piece.has_moved = True
                        chess_board.board[target_row][target_col] = piece
                        
                        chess_board.current_turn = Color.WHITE
                        chess_board.selected_piece = None
                        chess_board.valid_moves = []
                
                last_ai_move_time = current_time
                
            except Exception as e:
                ai_error_message = f"AI Error: {str(e)}"
                logger.error(f"AI error: {e}")
                ai_enabled = False
        
        # Draw everything
        screen.fill(BLACK)
        chess_board.draw(screen, piece_images)
        
        # Draw active powerup indicators
        y_offset = 10
        for powerup in chess_board.powerup_system.active_powerups:
            if powerup == PowerUpType.PAWN_FORWARD_CAPTURE:
                text = "Active: Pawns can capture forward"
                color = (240, 180, 100)
            elif powerup == PowerUpType.KNIGHT_EXTENDED_RANGE:
                text = "Active: Knights move further"
                color = (100, 180, 240)
            elif powerup == PowerUpType.RANDOM_PIECE_REMOVAL:
                # This one doesn't need a persistent indicator since it's one-time use
                continue
            else:
                continue
                
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (10, y_offset))
            y_offset += 25
        
        # Show move counter
        move_text = f"White Moves: {chess_board.powerup_system.white_moves_count} (Power-up every 3 moves)"
        move_surface = font.render(move_text, True, (200, 200, 200))
        screen.blit(move_surface, (10, HEIGHT - 30))
        
        # Show AI status and difficulty
        if ai is not None and hasattr(ai, 'difficulty'):
            ai_text = f"Stockfish AI: {'ON' if ai_enabled else 'OFF'} (Level {ai.difficulty}) - Press A to toggle"
            ai_color = (200, 200, 200) if ai_enabled else (150, 150, 150)
        else:
            ai_text = "Stockfish AI: Not available"
            ai_color = (255, 100, 100)
        
        ai_surface = font.render(ai_text, True, ai_color)
        screen.blit(ai_surface, (WIDTH - ai_surface.get_width() - 10, HEIGHT - 30))
        
        # Show key commands
        keys_text = "R: Reset Game"
        keys_surface = font.render(keys_text, True, (180, 180, 180))
        screen.blit(keys_surface, (WIDTH - keys_surface.get_width() - 10, HEIGHT - 55))
        
        # Display error message if there is one
        if ai_error_message:
            error_surface = font.render(ai_error_message, True, (255, 100, 100))
            screen.blit(error_surface, (WIDTH // 2 - error_surface.get_width() // 2, 40))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    # Clean up
    if ai is not None and hasattr(ai, 'close'):
        ai.close()  # Clean up Stockfish process
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()