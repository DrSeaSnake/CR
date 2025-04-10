from enum import Enum, auto
import random
import pygame
from constants import *

class PowerUpType(Enum):
    PAWN_FORWARD_CAPTURE = auto()  # Pawns can capture forward
    KNIGHT_EXTENDED_RANGE = auto()  # Knights can jump an extra square
    RANDOM_PIECE_REMOVAL = auto()   # Remove a random piece

class PowerUpSystem:
    def __init__(self):
        self.white_moves_count = 0
        self.active_powerups = set()
        self.show_powerup_selection = False
        self.selected_powerup = None
        self.buttons = []
        self.font = pygame.font.SysFont("Arial", 18)
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.removed_piece_message = None
        self.removed_piece_timer = 0
        
        # Create buttons for each powerup
        button_width = 200
        button_height = 80
        button_spacing = 20
        
        total_width = 3 * button_width + 2 * button_spacing
        start_x = (WIDTH - total_width) // 2
        start_y = HEIGHT // 2 - button_height // 2
        
        self.buttons = [
            {
                "rect": pygame.Rect(start_x, start_y, button_width, button_height),
                "powerup": PowerUpType.PAWN_FORWARD_CAPTURE,
                "text": "Pawns can capture forward",
                "color": (240, 180, 100)
            },
            {
                "rect": pygame.Rect(start_x + button_width + button_spacing, start_y, button_width, button_height),
                "powerup": PowerUpType.KNIGHT_EXTENDED_RANGE,
                "text": "Knights move further",
                "color": (100, 180, 240)
            },
            {
                "rect": pygame.Rect(start_x + 2 * (button_width + button_spacing), start_y, button_width, button_height),
                "powerup": PowerUpType.RANDOM_PIECE_REMOVAL,
                "text": "Remove random piece",
                "color": (240, 100, 100)
            }
        ]
    
    def increment_move_counter(self):
        """Increment the move counter for White"""
        self.white_moves_count += 1
        
        # Check if it's time to show powerup selection
        if self.white_moves_count % 3 == 0:
            self.show_powerup_selection = True
    
    def handle_click(self, pos):
        """Handle clicks on the powerup selection UI"""
        if not self.show_powerup_selection:
            return False
        
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                self.selected_powerup = button["powerup"]
                self.active_powerups.add(button["powerup"])
                self.show_powerup_selection = False
                return True
        
        return False
    
    def set_removed_piece_message(self, piece):
        """Set a message about which piece was removed"""
        if piece:
            color = "White" if piece.color.name == "WHITE" else "Black"
            piece_type = piece.piece_type.name.capitalize()
            self.removed_piece_message = f"Removed a {color} {piece_type}!"
            self.removed_piece_timer = 180  # Display for about 3 seconds at 60 FPS
    
    def update(self):
        """Update timers and states"""
        if self.removed_piece_timer > 0:
            self.removed_piece_timer -= 1
            if self.removed_piece_timer <= 0:
                self.removed_piece_message = None
    
    def draw(self, screen):
        """Draw the powerup selection UI if active"""
        if self.show_powerup_selection:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Semi-transparent black
            screen.blit(overlay, (0, 0))
            
            # Draw title
            title = self.title_font.render("Select a Power-Up!", True, WHITE)
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            screen.blit(title, title_rect)
            
            # Draw buttons
            for button in self.buttons:
                pygame.draw.rect(screen, button["color"], button["rect"], border_radius=10)
                pygame.draw.rect(screen, WHITE, button["rect"], 2, border_radius=10)  # Border
                
                # Wrap text to fit in button
                words = button["text"].split()
                lines = []
                current_line = []
                
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    test_width = self.font.size(test_line)[0]
                    
                    if test_width < button["rect"].width - 20:
                        current_line.append(word)
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                # Draw the text
                y_offset = button["rect"].centery - ((len(lines) * self.font.get_height()) // 2)
                for i, line in enumerate(lines):
                    text = self.font.render(line, True, BLACK)
                    text_rect = text.get_rect(center=(button["rect"].centerx, y_offset + i * self.font.get_height()))
                    screen.blit(text, text_rect)
        
        # Draw removed piece message if active
        if self.removed_piece_message:
            msg_surface = self.title_font.render(self.removed_piece_message, True, (255, 50, 50))
            msg_rect = msg_surface.get_rect(center=(WIDTH // 2, 40))
            # Add a background for better visibility
            bg_rect = msg_rect.inflate(20, 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.fill((0, 0, 0))
            bg_surface.set_alpha(180)
            screen.blit(bg_surface, bg_rect)
            screen.blit(msg_surface, msg_rect)