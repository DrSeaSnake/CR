from enum import Enum, auto
import random
import pygame
from constants import *
from pieces import Color

class PowerUpType(Enum):
    # Permanent powerups
    PAWN_FORWARD_CAPTURE = auto()  # Pawns can capture forward
    KNIGHT_EXTENDED_RANGE = auto()  # Knights can jump an extra square
    
    # One-time use powerups
    RANDOM_PIECE_REMOVAL = auto()   # Remove a random piece
    
    # Consumable powerups
    POISONED_PAWN = auto()  # When pawn is captured, creates a poison cloud

class PoisonCloud:
    def __init__(self, center_position, duration=3):
        """
        Initialize a poison cloud centered at the given position.
        
        Args:
            center_position (tuple): The (row, col) position of the cloud center
            duration (int): How many full turn cycles the cloud lasts before killing pieces
        """
        self.center_position = center_position
        self.total_duration = duration
        self.turns_remaining = duration
        
        # Track which turn this cloud was created on
        self.created_on_turn_count = 0
        self.last_decremented_on_turn_count = 0
        
        # Calculate the 3x3 grid affected by the cloud
        self.affected_squares = []
        center_row, center_col = center_position
        
        for row_offset in [-1, 0, 1]:
            for col_offset in [-1, 0, 1]:
                row = center_row + row_offset
                col = center_col + col_offset
                # Check if position is valid (within board bounds)
                if 0 <= row < 8 and 0 <= col < 8:
                    self.affected_squares.append((row, col))

class PowerUpSystem:
    def __init__(self):
        self.white_moves_count = 0
        self.active_powerups = set()
        self.show_powerup_selection = False
        self.selected_powerup = None
        
        # Consumable powerups
        self.consumables = []
        self.selecting_pawn_for_poison = False
        self.poisoned_pawns = []  # Store which pawns are poisoned
        self.poison_clouds = []   # Active poison clouds
        
        # UI elements
        self.buttons = []
        self.consumable_buttons = []
        self.font = pygame.font.SysFont("Arial", 18)
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 14)
        self.removed_piece_message = None
        self.removed_piece_timer = 0
        self.status_message = None
        self.status_timer = 0
        
        # Available powerups
        self.available_powerups = [
            {
                "powerup": PowerUpType.PAWN_FORWARD_CAPTURE,
                "text": "Pawns can capture forward",
                "color": (240, 180, 100),
                "type": "permanent"
            },
            {
                "powerup": PowerUpType.KNIGHT_EXTENDED_RANGE,
                "text": "Knights move further",
                "color": (100, 180, 240),
                "type": "permanent"
            },
            {
                "powerup": PowerUpType.RANDOM_PIECE_REMOVAL,
                "text": "Remove random piece",
                "color": (240, 100, 100),
                "type": "one-time"
            },
            {
                "powerup": PowerUpType.POISONED_PAWN,
                "text": "Poisoned Pawn",
                "color": (120, 220, 120),
                "type": "consumable"
            }
        ]
        
        # The current power-ups to choose from (will be randomly selected)
        self.current_powerup_choices = []
    
    def increment_move_counter(self):
        """Increment the move counter for White"""
        self.white_moves_count += 1
        
        # Check if it's time to show powerup selection (every 5 moves)
        if self.white_moves_count % 5 == 0:
            # Select 2 random powerups from the available ones
            self.current_powerup_choices = random.sample(self.available_powerups, 2)
            self._create_powerup_buttons()
            self.show_powerup_selection = True
    
    def _create_powerup_buttons(self):
        """Create buttons for the current powerup choices"""
        self.buttons = []
        
        # For 2 buttons, center them
        button_width = 200
        button_height = 80
        button_spacing = 40
        
        total_width = 2 * button_width + button_spacing
        start_x = (WIDTH - total_width) // 2
        start_y = HEIGHT // 2 - button_height // 2
        
        # Create a button for each of the chosen powerups
        for i, powerup_info in enumerate(self.current_powerup_choices):
            x = start_x + i * (button_width + button_spacing)
            self.buttons.append({
                "rect": pygame.Rect(x, start_y, button_width, button_height),
                "powerup": powerup_info["powerup"],
                "text": powerup_info["text"],
                "color": powerup_info["color"],
                "type": powerup_info["type"]
            })
    
    def create_consumable_buttons(self, sidebar_start_x, sidebar_width):
        """Create buttons for consumable items in the sidebar"""
        self.consumable_buttons = []
        
        button_height = 30
        button_spacing = 5
        y_position = 330  # Position below active powerups section
        
        for i, consumable in enumerate(self.consumables):
            if consumable["powerup"] == PowerUpType.POISONED_PAWN:
                text = "Use Poisoned Pawn"
                color = (120, 220, 120)
            else:
                # Generic text for future consumables
                text = f"Use {consumable['powerup'].name}"
                color = (180, 180, 180)
            
            self.consumable_buttons.append({
                "rect": pygame.Rect(sidebar_start_x, y_position + i * (button_height + button_spacing), 
                                    sidebar_width, button_height),
                "powerup": consumable["powerup"],
                "text": text,
                "color": color,
                "index": i  # Store index to easily remove from consumables list when used
            })
    
    def handle_click(self, pos):
        """Handle clicks on the powerup selection UI"""
        if self.selecting_pawn_for_poison:
            # This click will be handled by the board to select a pawn
            return False
            
        if not self.show_powerup_selection:
            return False
        
        # Debug info
        print(f"Handling powerup click at {pos}")
        
        for i, button in enumerate(self.buttons):
            print(f"Button {i}: Rect={button['rect']}, Contains click={button['rect'].collidepoint(pos)}")
            if button["rect"].collidepoint(pos):
                print(f"Selected powerup: {button['powerup']}")
                self.selected_powerup = button["powerup"]
                
                # Handle the powerup based on its type
                if button["type"] == "permanent":
                    # Add it to active powerups set
                    self.active_powerups.add(button["powerup"])
                elif button["type"] == "consumable":
                    # Add it to consumables list
                    self.consumables.append({
                        "powerup": button["powerup"],
                        "text": button["text"]
                    })
                    self.set_status_message(f"Added {button['text']} to consumables")
                # One-time powerups will be handled in the main game loop
                
                self.show_powerup_selection = False
                return True
        
        # If we get here, the click wasn't on any button
        print("Click wasn't on any powerup button")
        return False
    
    def handle_consumable_click(self, pos):
        """Handle clicks on consumable buttons in the sidebar"""
        for i, button in enumerate(self.consumable_buttons):
            if button["rect"].collidepoint(pos):
                powerup = button["powerup"]
                index = button["index"]
                
                if powerup == PowerUpType.POISONED_PAWN:
                    # Start the process of selecting a pawn to poison
                    self.selecting_pawn_for_poison = True
                    self.set_status_message("Select a pawn to poison")
                    # Remove it from consumables (will be added back if selection is cancelled)
                    self.consumables.pop(index)
                    # Regenerate consumable buttons
                    self.consumable_buttons = []
                    return True
                
                # Handle other consumable types here
                
                return True
        return False
    
    def cancel_pawn_selection(self):
        """Cancel the pawn selection and add the powerup back to consumables"""
        if self.selecting_pawn_for_poison:
            self.selecting_pawn_for_poison = False
            self.consumables.append({
                "powerup": PowerUpType.POISONED_PAWN,
                "text": "Poisoned Pawn"
            })
            self.set_status_message("Poisoned Pawn selection cancelled")
    
    def select_pawn_for_poison(self, pawn):
        """Mark a pawn as poisoned"""
        self.poisoned_pawns.append(pawn)
        self.selecting_pawn_for_poison = False
        self.set_status_message(f"Pawn at {pawn.position} is now poisoned")
    
    def check_pawn_capture(self, captured_piece, position):
        """
        Check if a captured piece was a poisoned pawn and create a poison cloud if it was
        
        Args:
            captured_piece: The piece that was captured
            position: The (row, col) position where the piece was captured
        """
        if captured_piece in self.poisoned_pawns:
            # Create a poison cloud at the capture position
            self.poison_clouds.append(PoisonCloud(position))
            # Remove the pawn from the poisoned pawns list
            self.poisoned_pawns.remove(captured_piece)
            self.set_status_message(f"Poison cloud created at {position}!")
    
    def create_poison_cloud(self, position, turn_count):
        """
        Create a new poison cloud and set its turn counter properly
        
        Args:
            position: The (row, col) where the cloud should be created
            turn_count: The current game turn count
        """
        cloud = PoisonCloud(position)
        cloud.created_on_turn_count = turn_count
        cloud.last_decremented_on_turn_count = turn_count
        self.poison_clouds.append(cloud)
        self.set_status_message(f"Poison cloud created at {position}! Will trigger in {cloud.turns_remaining} turns.")
        return cloud
    
    def update_poison_clouds(self, turn_count, chess_board):
        """
        Update all poison clouds based on the current turn count
        
        Args:
            turn_count: The current game turn count
            chess_board: The chess board object to modify pieces
            
        Returns:
            A list of pieces killed by poison clouds
        """
        if not self.poison_clouds:
            return []
        
        clouds_to_remove = []
        killed_pieces = []
        
        for cloud in self.poison_clouds:
            # Only update once per turn cycle (every 2 moves - White & Black)
            # AND only if current turn = White's turn (after Black has moved)
            if (turn_count - cloud.last_decremented_on_turn_count >= 2 and
                chess_board.current_turn == Color.WHITE):
                
                # Update its last decremented time
                cloud.last_decremented_on_turn_count = turn_count
                
                # Decrement the counter
                cloud.turns_remaining -= 1
                print(f"Decreasing cloud at {cloud.center_position} to {cloud.turns_remaining} turns remaining")
                
                # Check if the cloud should trigger
                if cloud.turns_remaining <= 0:
                    print(f"Cloud at {cloud.center_position} is triggering!")
                    # Kill all pieces in the cloud area
                    for pos in cloud.affected_squares:
                        row, col = pos
                        if chess_board.board[row][col] is not None:
                            piece = chess_board.board[row][col]
                            piece_name = f"{piece.color.name} {piece.piece_type.name}"
                            killed_pieces.append(piece_name)
                            chess_board.board[row][col] = None
                    
                    # Mark for removal
                    clouds_to_remove.append(cloud)
        
        # Remove triggered clouds
        for cloud in clouds_to_remove:
            self.poison_clouds.remove(cloud)
        
        return killed_pieces
    
    def set_removed_piece_message(self, piece):
        """Set a message about which piece was removed"""
        if piece:
            color = "White" if piece.color.name == "WHITE" else "Black"
            piece_type = piece.piece_type.name.capitalize()
            self.removed_piece_message = f"Removed a {color} {piece_type}!"
            self.removed_piece_timer = 180  # Display for about 3 seconds at 60 FPS
    
    def set_status_message(self, message, duration=180):
        """Set a status message to display"""
        self.status_message = message
        self.status_timer = duration  # Display for about 3 seconds at 60 FPS
    
    def update(self):
        """Update timers and states"""
        if self.removed_piece_timer > 0:
            self.removed_piece_timer -= 1
            if self.removed_piece_timer <= 0:
                self.removed_piece_message = None
                
        if self.status_timer > 0:
            self.status_timer -= 1
            if self.status_timer <= 0:
                self.status_message = None
    
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
            
        # Draw status message if active
        if self.status_message:
            msg_surface = self.font.render(self.status_message, True, (220, 220, 100))
            msg_rect = msg_surface.get_rect(center=(WIDTH // 2, 70))
            # Add a background for better visibility
            bg_rect = msg_rect.inflate(20, 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.fill((0, 0, 0))
            bg_surface.set_alpha(180)
            screen.blit(bg_surface, bg_rect)
            screen.blit(msg_surface, msg_rect)
    
    def draw_consumables(self, screen, sidebar_start_x, sidebar_width):
        """Draw the consumables section in the sidebar"""
        consumables_title = self.font.render("Consumables:", True, SIDEBAR_TEXT)
        screen.blit(consumables_title, (sidebar_start_x, 300))
        
        if not self.consumables:
            no_items_text = self.small_font.render("No consumable items", True, (150, 150, 150))
            screen.blit(no_items_text, (sidebar_start_x, 330))
        else:
            # Create buttons if they don't exist
            if not self.consumable_buttons:
                self.create_consumable_buttons(sidebar_start_x, sidebar_width)
                
            # Draw the buttons
            for button in self.consumable_buttons:
                pygame.draw.rect(screen, button["color"], button["rect"], border_radius=5)
                pygame.draw.rect(screen, (200, 200, 200), button["rect"], 1, border_radius=5)  # Border
                
                text_surf = self.small_font.render(button["text"], True, BLACK)
                text_rect = text_surf.get_rect(center=button["rect"].center)
                screen.blit(text_surf, text_rect)
    
    def draw_poison_clouds(self, screen):
        """Draw poison cloud indicators on the board"""
        if not self.poison_clouds:
            return
            
        for cloud in self.poison_clouds:
            # Draw semi-transparent green squares for poison clouds
            for row, col in cloud.affected_squares:
                # Create a surface for this square
                cloud_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                
                # Very bright, noticeable green color
                cloud_color = (0, 255, 0, 150)  # Bright green with good opacity
                
                # Create a pulsing effect for extra visibility
                pulse = (pygame.time.get_ticks() % 1000) / 1000.0
                alpha = int(100 + 50 * pulse)  # Pulsing opacity between 100-150
                
                # Fill the square with the cloud color
                cloud_surface.fill((0, 255, 0, alpha))
                
                # Add a bright, obvious border
                border_width = 3
                pygame.draw.rect(cloud_surface, (255, 255, 255, 200), 
                                (0, 0, SQUARE_SIZE, SQUARE_SIZE), border_width)
                
                # Add countdown in the center square
                if (row, col) == cloud.center_position:
                    # Add a dark background circle for the number
                    circle_radius = SQUARE_SIZE // 2.5
                    pygame.draw.circle(cloud_surface, (0, 0, 0, 200), 
                                      (SQUARE_SIZE // 2, SQUARE_SIZE // 2), circle_radius)
                    
                    # Draw a large, very visible countdown number
                    font = pygame.font.SysFont("Arial", 48, bold=True)
                    text = font.render(str(cloud.turns_remaining), True, (255, 255, 255))
                    text_rect = text.get_rect(center=(SQUARE_SIZE // 2, SQUARE_SIZE // 2))
                    cloud_surface.blit(text, text_rect)
                
                # Blit the cloud surface onto the screen
                screen.blit(cloud_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
    
    def draw_poisoned_pawns(self, screen):
        """Draw indicators for poisoned pawns"""
        for pawn in self.poisoned_pawns:
            row, col = pawn.position
            indicator_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            
            # Draw a green border around the pawn
            border_width = 3
            border_color = (0, 220, 0, 200)  # Bright green with some transparency
            pygame.draw.rect(indicator_surface, border_color, 
                            (0, 0, SQUARE_SIZE, SQUARE_SIZE), border_width)
            
            # Draw a small poison symbol in the corner
            pygame.draw.circle(indicator_surface, border_color, 
                              (SQUARE_SIZE - 10, 10), 5)
            
            screen.blit(indicator_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))