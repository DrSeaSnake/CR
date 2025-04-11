import pygame
import sys
import time
import logging
import random
from constants import *
from board import ChessBoard
from utils import load_piece_images
from powerups import PowerUpType
from pieces import Color, PieceType, Piece

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChessRoguelike")

class Button:
    def __init__(self, x, y, width, height, text, action, font, color=SIDEBAR_BUTTON, hover_color=SIDEBAR_BUTTON_HOVER, text_color=SIDEBAR_BUTTON_TEXT):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
    
    def draw(self, screen):
        # Draw button background with rounded corners
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=BUTTON_RADIUS)
        
        # Draw button text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.action()
                return True
        return False

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up the display (now including sidebar)
    screen = pygame.display.set_mode((TOTAL_WIDTH, HEIGHT))
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
    
    # Track total moves
    total_moves = 0
    
    # Create fonts
    title_font = pygame.font.SysFont("Arial", 22, bold=True)
    regular_font = pygame.font.SysFont("Arial", 16)
    small_font = pygame.font.SysFont("Arial", 14)
    
    # Create buttons
    buttons = []
    
    def toggle_ai():
        nonlocal ai_enabled
        if ai is not None:
            ai_enabled = not ai_enabled
            logger.info(f"AI: {'enabled' if ai_enabled else 'disabled'}")
    
    def reset_game():
        nonlocal chess_board, total_moves, ai_error_message
        chess_board = ChessBoard()
        total_moves = 0
        ai_error_message = None
        logger.info("Game reset")
    
    # Initialize buttons (will add them after we have the screen)
    
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
    
    # Create sidebar buttons
    sidebar_start_x = WIDTH + BUTTON_MARGIN
    sidebar_width = SIDEBAR_WIDTH - (2 * BUTTON_MARGIN)
    
    # Add buttons after the screen is created
    reset_button = Button(
        sidebar_start_x, 
        HEIGHT - (BUTTON_HEIGHT + BUTTON_MARGIN) * 2, 
        sidebar_width, 
        BUTTON_HEIGHT, 
        "Reset Game", 
        reset_game, 
        regular_font
    )
    
    ai_button = Button(
        sidebar_start_x, 
        HEIGHT - (BUTTON_HEIGHT + BUTTON_MARGIN), 
        sidebar_width, 
        BUTTON_HEIGHT, 
        "Toggle AI", 
        toggle_ai, 
        regular_font
    )
    
    buttons = [reset_button, ai_button]
    
    running = True
    while running:
        current_time = time.time()
        mouse_pos = pygame.mouse.get_pos()
        
        # Check button hover
        for button in buttons:
            button.check_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and ai is not None:
                    toggle_ai()
                elif event.key == pygame.K_r:
                    reset_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if buttons were clicked
                button_clicked = False
                for button in buttons:
                    if button.handle_event(event):
                        button_clicked = True
                        break
                
                if button_clicked:
                    continue
                
                if event.button == 1:  # Left mouse button
                    # Adjust click position if it's in the board area
                    board_click = event.pos
                    if board_click[0] <= WIDTH:  # Only if clicking in the board area
                        # First check if this is a powerup selection click
                        if chess_board.powerup_system.show_powerup_selection:
                            logger.info(f"Detected click during powerup selection at {board_click}")
                            if chess_board.powerup_system.handle_click(board_click):
                                logger.info("Powerup selected")
                                # If random piece removal was selected, apply it immediately
                                if chess_board.powerup_system.selected_powerup == PowerUpType.RANDOM_PIECE_REMOVAL:
                                    removed_piece = chess_board.remove_random_piece()
                                    chess_board.powerup_system.set_removed_piece_message(removed_piece)
                                    chess_board.powerup_system.selected_powerup = None
                        
                        # Only allow player to move white pieces when it's their turn and no powerup selection is active
                        elif chess_board.current_turn == Color.WHITE and not chess_board.powerup_system.show_powerup_selection:
                            old_turn = chess_board.current_turn
                            chess_board.handle_click(board_click)
                            
                            # Check if a move was made
                            if chess_board.current_turn != old_turn:
                                # A move was made, increment total moves
                                total_moves += 1
                                # Clear error messages
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
                    
                    # Store captured piece
                    captured_piece = chess_board.board[target_row][target_col]
                    
                    # Clear the old position
                    chess_board.board[row][col] = None
                    
                    # Move to the new position
                    piece.position = target_pos
                    piece.has_moved = True
                    chess_board.board[target_row][target_col] = piece
                    
                    # Update game state
                    chess_board.last_move = (piece, (row, col), target_pos)
                    
                    # Increment total moves
                    total_moves += 1
                    
                    # Check for powerup activation - increment white's move counter
                    # This is needed for proper powerup handling
                    if chess_board.current_turn == Color.WHITE:
                        chess_board.powerup_system.increment_move_counter()
                    
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
                        
                        # Update game state
                        chess_board.last_move = (piece, (row, col), random_move)
                        
                        # Increment total moves
                        total_moves += 1
                        
                        chess_board.current_turn = Color.WHITE
                        chess_board.selected_piece = None
                        chess_board.valid_moves = []
                
                last_ai_move_time = current_time
                
            except Exception as e:
                ai_error_message = f"AI Error: {str(e)}"
                logger.error(f"AI error: {e}")
                ai_enabled = False
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Draw the chess board
        chess_board.draw(screen, piece_images)
        
        # Draw the sidebar
        pygame.draw.rect(screen, SIDEBAR_BACKGROUND, (WIDTH, 0, SIDEBAR_WIDTH, HEIGHT))
        
        # Draw sidebar title
        title_surf = title_font.render("CHESS ROGUELIKE", True, SIDEBAR_TEXT)
        screen.blit(title_surf, (WIDTH + (SIDEBAR_WIDTH - title_surf.get_width()) // 2, 20))
        
        # Draw divider
        pygame.draw.line(screen, SIDEBAR_DIVIDER, (WIDTH, 50), (TOTAL_WIDTH, 50), 2)
        
        # Draw move counters
        move_title = regular_font.render("Game Statistics:", True, SIDEBAR_TEXT)
        screen.blit(move_title, (WIDTH + 10, 70))
        
        total_moves_text = regular_font.render(f"Total Moves: {total_moves}", True, SIDEBAR_TEXT)
        screen.blit(total_moves_text, (WIDTH + 10, 100))
        
        # Calculate moves until next powerup
        moves_until_powerup = 3 - (chess_board.powerup_system.white_moves_count % 3)
        if moves_until_powerup == 3:
            moves_until_powerup = 0
            
        powerup_text = regular_font.render(f"Next Powerup in: {moves_until_powerup}", True, SIDEBAR_TEXT)
        screen.blit(powerup_text, (WIDTH + 10, 130))
        
        current_turn_text = regular_font.render(f"Current Turn: {'White' if chess_board.current_turn == Color.WHITE else 'Black'}", True, SIDEBAR_TEXT)
        screen.blit(current_turn_text, (WIDTH + 10, 160))
        
        # Draw divider before active powerups
        pygame.draw.line(screen, SIDEBAR_DIVIDER, (WIDTH, 190), (TOTAL_WIDTH, 190), 2)
        
        # Draw active powerup indicators
        active_title = regular_font.render("Active Powerups:", True, SIDEBAR_TEXT)
        screen.blit(active_title, (WIDTH + 10, 210))
        
        y_offset = 240
        has_active_powerups = False
        
        for powerup in chess_board.powerup_system.active_powerups:
            if powerup == PowerUpType.PAWN_FORWARD_CAPTURE:
                text = "Pawns can capture forward"
                color = (240, 180, 100)
                has_active_powerups = True
            elif powerup == PowerUpType.KNIGHT_EXTENDED_RANGE:
                text = "Knights move further"
                color = (100, 180, 240)
                has_active_powerups = True
            elif powerup == PowerUpType.RANDOM_PIECE_REMOVAL:
                # This one doesn't need a persistent indicator since it's one-time use
                continue
            else:
                continue
                
            text_surface = regular_font.render(text, True, color)
            screen.blit(text_surface, (WIDTH + 10, y_offset))
            y_offset += 30
        
        if not has_active_powerups:
            no_powerups_text = small_font.render("No active powerups", True, (150, 150, 150))
            screen.blit(no_powerups_text, (WIDTH + 10, y_offset))
        
        # Draw divider before controls
        pygame.draw.line(screen, SIDEBAR_DIVIDER, (WIDTH, HEIGHT - 150), (TOTAL_WIDTH, HEIGHT - 150), 2)
        
        # Draw AI status
        ai_status_title = regular_font.render("AI Status:", True, SIDEBAR_TEXT)
        screen.blit(ai_status_title, (WIDTH + 10, HEIGHT - 130))
        
        if ai is not None and hasattr(ai, 'difficulty'):
            ai_text = f"Stockfish: {'ON' if ai_enabled else 'OFF'} (Level {ai.difficulty})"
            ai_color = (120, 200, 120) if ai_enabled else (200, 120, 120)
        else:
            ai_text = "Stockfish: Not available"
            ai_color = (200, 120, 120)
        
        ai_surface = regular_font.render(ai_text, True, ai_color)
        screen.blit(ai_surface, (WIDTH + 10, HEIGHT - 100))
        
        # Draw buttons
        for button in buttons:
            button.draw(screen)
        
        # Display error message if there is one
        if ai_error_message:
            error_surface = regular_font.render(ai_error_message, True, (255, 100, 100))
            screen.blit(error_surface, (WIDTH // 2 - error_surface.get_width() // 2, 40))
        
        # Draw removed piece message if active
        if hasattr(chess_board.powerup_system, 'removed_piece_message') and chess_board.powerup_system.removed_piece_message:
            msg_surface = regular_font.render(chess_board.powerup_system.removed_piece_message, True, (255, 50, 50))
            msg_rect = msg_surface.get_rect(center=(WIDTH // 2, 40))
            # Add a background for better visibility
            bg_rect = msg_rect.inflate(20, 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.fill((0, 0, 0))
            bg_surface.set_alpha(180)
            screen.blit(bg_surface, bg_rect)
            screen.blit(msg_surface, msg_rect)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    # Clean up
    if ai is not None and hasattr(ai, 'close'):
        ai.close()  # Clean up Stockfish process
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()