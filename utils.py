import os
import pygame
from constants import SQUARE_SIZE

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, 'assets')

# Load piece images and scale them
def load_piece_images():
    pieces = {}
    # Create assets directory if it doesn't exist
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)
        print(f"Created assets directory at: {ASSETS_DIR}")
    
    for color in ["w", "b"]:
        for piece in ["p", "n", "b", "r", "q", "k"]:
            key = color + piece
            filename = os.path.join(ASSETS_DIR, f"{key}.png")
            try:
                print(f"Trying to load: {filename}")
                img = pygame.image.load(filename)
                img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
                pieces[key] = img
                print(f"Successfully loaded {filename}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")
                # If image loading fails, create placeholder pieces
                pieces[key] = create_placeholder_piece(color, piece)
    return pieces

def create_placeholder_piece(color, piece):
    # Create a placeholder surface for pieces when images aren't available
    surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    bg_color = (200, 200, 200) if color == "w" else (70, 70, 70)
    
    # Draw circle
    pygame.draw.circle(surface, bg_color, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//2.5)
    
    # Draw piece type identifier
    font = pygame.font.SysFont("Arial", 32, bold=True)
    text = font.render(piece.upper(), True, (0, 0, 0) if color == "w" else (255, 255, 255))
    text_rect = text.get_rect(center=(SQUARE_SIZE//2, SQUARE_SIZE//2))
    surface.blit(text, text_rect)
    
    return surface