import pygame
import sys
from constants import WIDTH, HEIGHT, FPS, BLACK
from board import ChessBoard
from utils import load_piece_images

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()
    
    # Load piece images
    piece_images = load_piece_images()
    
    # Create chess board
    chess_board = ChessBoard()
    
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
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()