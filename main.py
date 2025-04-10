import pygame
import sys
from constants import WIDTH, HEIGHT, FPS, BLACK
from board import ChessBoard
from utils import load_piece_images
from powerups import PowerUpType

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
    
    # Create font for powerup indicators
    font = pygame.font.SysFont("Arial", 16)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    chess_board.handle_click(event.pos)
        
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
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()