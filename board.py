import pygame
from constants import *
from pieces import Piece, PieceType, Color

class ChessBoard:
    def __init__(self):
        self.reset_board()
        self.selected_piece = None
        self.valid_moves = []
        self.current_turn = Color.WHITE
        self.last_move = None
        self.en_passant_target = None

    def reset_board(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Setup pawns
        for col in range(BOARD_SIZE):
            self.board[1][col] = Piece(PieceType.PAWN, Color.BLACK, (1, col))
            self.board[6][col] = Piece(PieceType.PAWN, Color.WHITE, (6, col))
        
        # Setup back rank for black
        back_rank_black = [
            Piece(PieceType.ROOK, Color.BLACK, (0, 0)),
            Piece(PieceType.KNIGHT, Color.BLACK, (0, 1)),
            Piece(PieceType.BISHOP, Color.BLACK, (0, 2)),
            Piece(PieceType.QUEEN, Color.BLACK, (0, 3)),
            Piece(PieceType.KING, Color.BLACK, (0, 4)),
            Piece(PieceType.BISHOP, Color.BLACK, (0, 5)),
            Piece(PieceType.KNIGHT, Color.BLACK, (0, 6)),
            Piece(PieceType.ROOK, Color.BLACK, (0, 7))
        ]
        
        # Setup back rank for white
        back_rank_white = [
            Piece(PieceType.ROOK, Color.WHITE, (7, 0)),
            Piece(PieceType.KNIGHT, Color.WHITE, (7, 1)),
            Piece(PieceType.BISHOP, Color.WHITE, (7, 2)),
            Piece(PieceType.QUEEN, Color.WHITE, (7, 3)),
            Piece(PieceType.KING, Color.WHITE, (7, 4)),
            Piece(PieceType.BISHOP, Color.WHITE, (7, 5)),
            Piece(PieceType.KNIGHT, Color.WHITE, (7, 6)),
            Piece(PieceType.ROOK, Color.WHITE, (7, 7))
        ]
        
        # Place the pieces on the board
        for col, piece in enumerate(back_rank_black):
            self.board[0][col] = piece
        
        for col, piece in enumerate(back_rank_white):
            self.board[7][col] = piece

    def is_valid_position(self, row, col):
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def get_valid_moves(self, piece):
        moves = []
        row, col = piece.position
        
        if piece.piece_type == PieceType.PAWN:
            moves = self.get_pawn_moves(piece)
        elif piece.piece_type == PieceType.KNIGHT:
            moves = self.get_knight_moves(piece)
        elif piece.piece_type == PieceType.BISHOP:
            moves = self.get_bishop_moves(piece)
        elif piece.piece_type == PieceType.ROOK:
            moves = self.get_rook_moves(piece)
        elif piece.piece_type == PieceType.QUEEN:
            moves = self.get_queen_moves(piece)
        elif piece.piece_type == PieceType.KING:
            moves = self.get_king_moves(piece)
        
        # Filter out moves that would leave the king in check
        legal_moves = []
        for move in moves:
            if not self.would_move_cause_check(piece, move):
                legal_moves.append(move)
        
        return legal_moves

    def get_pawn_moves(self, piece):
        moves = []
        row, col = piece.position
        direction = -1 if piece.color == Color.WHITE else 1
        
        # Forward move (one square)
        new_row = row + direction
        if self.is_valid_position(new_row, col) and self.board[new_row][col] is None:
            moves.append((new_row, col))
            
            # Double move from starting position
            start_row = 6 if piece.color == Color.WHITE else 1
            if row == start_row:
                new_row = row + 2 * direction
                if self.is_valid_position(new_row, col) and self.board[new_row][col] is None:
                    moves.append((new_row, col))
        
        # Captures (diagonally)
        for col_offset in [-1, 1]:
            new_col = col + col_offset
            new_row = row + direction
            if self.is_valid_position(new_row, new_col):
                # Normal capture
                target = self.board[new_row][new_col]
                if target is not None and target.color != piece.color:
                    moves.append((new_row, new_col))
                
                # En passant capture
                if self.en_passant_target == (new_row, new_col):
                    moves.append((new_row, new_col))
        
        return moves

    def get_knight_moves(self, piece):
        moves = []
        row, col = piece.position
        
        # All possible knight moves
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for r_offset, c_offset in offsets:
            new_row, new_col = row + r_offset, col + c_offset
            if self.is_valid_position(new_row, new_col):
                target = self.board[new_row][new_col]
                if target is None or target.color != piece.color:
                    moves.append((new_row, new_col))
        
        return moves

    def get_bishop_moves(self, piece):
        moves = []
        row, col = piece.position
        
        # Diagonal directions
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for r_dir, c_dir in directions:
            for i in range(1, BOARD_SIZE):
                new_row, new_col = row + i * r_dir, col + i * c_dir
                if not self.is_valid_position(new_row, new_col):
                    break
                
                target = self.board[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != piece.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves

    def get_rook_moves(self, piece):
        moves = []
        row, col = piece.position
        
        # Horizontal and vertical directions
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        for r_dir, c_dir in directions:
            for i in range(1, BOARD_SIZE):
                new_row, new_col = row + i * r_dir, col + i * c_dir
                if not self.is_valid_position(new_row, new_col):
                    break
                
                target = self.board[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != piece.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves

    def get_queen_moves(self, piece):
        # Queen moves are a combination of rook and bishop moves
        return self.get_rook_moves(piece) + self.get_bishop_moves(piece)

    def get_king_moves(self, piece):
        moves = []
        row, col = piece.position
        
        # Regular king moves (one square in any direction)
        for r_offset in [-1, 0, 1]:
            for c_offset in [-1, 0, 1]:
                if r_offset == 0 and c_offset == 0:
                    continue
                
                new_row, new_col = row + r_offset, col + c_offset
                if self.is_valid_position(new_row, new_col):
                    target = self.board[new_row][new_col]
                    if target is None or target.color != piece.color:
                        moves.append((new_row, new_col))
        
        # Castling moves
        if not piece.has_moved and not self.is_king_in_check(piece.color):
            # Kingside castling
            if self.can_castle_kingside(piece.color):
                if piece.color == Color.WHITE:
                    moves.append((7, 6))  # White kingside
                else:
                    moves.append((0, 6))  # Black kingside
            
            # Queenside castling
            if self.can_castle_queenside(piece.color):
                if piece.color == Color.WHITE:
                    moves.append((7, 2))  # White queenside
                else:
                    moves.append((0, 2))  # Black queenside
        
        return moves

    def can_castle_kingside(self, color):
        # Check if king and kingside rook are in their initial positions and haven't moved
        row = 7 if color == Color.WHITE else 0
        king = self.board[row][4]
        rook = self.board[row][7]
        
        if king is None or rook is None:
            return False
        
        if king.piece_type != PieceType.KING or rook.piece_type != PieceType.ROOK:
            return False
        
        if king.has_moved or rook.has_moved:
            return False
        
        # Check if squares between king and rook are empty
        if self.board[row][5] is not None or self.board[row][6] is not None:
            return False
        
        # Check if king passes through or ends up in check
        if self.is_square_under_attack(row, 4, color) or \
           self.is_square_under_attack(row, 5, color) or \
           self.is_square_under_attack(row, 6, color):
            return False
        
        return True

    def can_castle_queenside(self, color):
        # Check if king and queenside rook are in their initial positions and haven't moved
        row = 7 if color == Color.WHITE else 0
        king = self.board[row][4]
        rook = self.board[row][0]
        
        if king is None or rook is None:
            return False
        
        if king.piece_type != PieceType.KING or rook.piece_type != PieceType.ROOK:
            return False
        
        if king.has_moved or rook.has_moved:
            return False
        
        # Check if squares between king and rook are empty
        if self.board[row][1] is not None or self.board[row][2] is not None or self.board[row][3] is not None:
            return False
        
        # Check if king passes through or ends up in check
        if self.is_square_under_attack(row, 4, color) or \
           self.is_square_under_attack(row, 3, color) or \
           self.is_square_under_attack(row, 2, color):
            return False
        
        return True

    def is_square_under_attack(self, row, col, friendly_color):
        # Check if the square at (row, col) is under attack by any piece of the opposite color
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board[r][c]
                if piece is not None and piece.color != friendly_color:
                    # For efficiency, we'll check specific piece types differently
                    if piece.piece_type == PieceType.PAWN:
                        # Pawns capture diagonally
                        direction = -1 if piece.color == Color.WHITE else 1
                        if r + direction == row and (c - 1 == col or c + 1 == col):
                            return True
                    elif piece.piece_type == PieceType.KING:
                        # King attacks one square in any direction
                        if abs(r - row) <= 1 and abs(c - col) <= 1:
                            return True
                    else:
                        # For other pieces, use their move pattern
                        valid_moves = self.get_moves_without_check_validation(piece)
                        if (row, col) in valid_moves:
                            return True
        return False

    def get_moves_without_check_validation(self, piece):
        # Get moves without validating for check (to avoid recursion)
        if piece.piece_type == PieceType.PAWN:
            return self.get_pawn_moves(piece)
        elif piece.piece_type == PieceType.KNIGHT:
            return self.get_knight_moves(piece)
        elif piece.piece_type == PieceType.BISHOP:
            return self.get_bishop_moves(piece)
        elif piece.piece_type == PieceType.ROOK:
            return self.get_rook_moves(piece)
        elif piece.piece_type == PieceType.QUEEN:
            return self.get_queen_moves(piece)
        elif piece.piece_type == PieceType.KING:
            # For king, exclude castling to avoid recursion
            moves = []
            row, col = piece.position
            
            for r_offset in [-1, 0, 1]:
                for c_offset in [-1, 0, 1]:
                    if r_offset == 0 and c_offset == 0:
                        continue
                    
                    new_row, new_col = row + r_offset, col + c_offset
                    if self.is_valid_position(new_row, new_col):
                        target = self.board[new_row][new_col]
                        if target is None or target.color != piece.color:
                            moves.append((new_row, new_col))
            return moves
        return []

    def is_king_in_check(self, color):
        # Find the king of the given color
        king_position = None
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece is not None and piece.color == color and piece.piece_type == PieceType.KING:
                    king_position = (row, col)
                    break
            if king_position:
                break
        
        if not king_position:
            return False  # No king found (shouldn't happen in a valid game)
        
        # Check if the king's position is under attack
        return self.is_square_under_attack(king_position[0], king_position[1], color)

    def would_move_cause_check(self, piece, target_pos):
        # Temporarily make the move and see if it leaves/puts the king in check
        row, col = piece.position
        target_row, target_col = target_pos
        
        # Store the original state
        original_piece = piece
        captured_piece = self.board[target_row][target_col]
        original_has_moved = piece.has_moved
        original_position = piece.position
        
        # Make the temporary move
        self.board[row][col] = None
        self.board[target_row][target_col] = piece
        piece.position = target_pos
        piece.has_moved = True
        
        # Special case for castling
        rook_original_pos = None
        rook_temp_pos = None
        rook = None
        
        if piece.piece_type == PieceType.KING and abs(col - target_col) > 1:
            # This is a castling move
            if target_col == 6:  # Kingside
                rook = self.board[row][7]
                rook_original_pos = (row, 7)
                rook_temp_pos = (row, 5)
                if rook:
                    self.board[row][7] = None
                    self.board[row][5] = rook
                    rook.position = rook_temp_pos
            else:  # Queenside
                rook = self.board[row][0]
                rook_original_pos = (row, 0)
                rook_temp_pos = (row, 3)
                if rook:
                    self.board[row][0] = None
                    self.board[row][3] = rook
                    rook.position = rook_temp_pos
        
        # Check if the king is in check after the move
        in_check = self.is_king_in_check(piece.color)
        
        # Restore the original state
        self.board[row][col] = original_piece
        self.board[target_row][target_col] = captured_piece
        piece.position = original_position
        piece.has_moved = original_has_moved
        
        # Restore rook position if this was a castling move
        if rook_original_pos and rook_temp_pos and rook:
            orig_row, orig_col = rook_original_pos
            temp_row, temp_col = rook_temp_pos
            self.board[orig_row][orig_col] = rook
            self.board[temp_row][temp_col] = None
            rook.position = rook_original_pos
        
        return in_check

    def move_piece(self, piece, target_pos):
        if not piece or target_pos not in self.valid_moves:
            return False
        
        row, col = piece.position
        target_row, target_col = target_pos
        
        # Check for en passant capture
        en_passant_capture = False
        if piece.piece_type == PieceType.PAWN and col != target_col and self.board[target_row][target_col] is None:
            en_passant_capture = True
        
        # Check for pawn double move (for en passant)
        pawn_double_move = False
        if piece.piece_type == PieceType.PAWN and abs(row - target_row) == 2:
            pawn_double_move = True
        
        # Reset en passant vulnerability for all pawns
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] and self.board[r][c].piece_type == PieceType.PAWN:
                    self.board[r][c].is_en_passant_vulnerable = False
        
        # Check for castling
        if piece.piece_type == PieceType.KING and abs(col - target_col) > 1:
            # This is a castling move
            direction = 1 if target_col > col else -1
            rook_col = 7 if direction > 0 else 0
            new_rook_col = 5 if direction > 0 else 3
            
            # Move the rook
            rook = self.board[row][rook_col]
            self.board[row][rook_col] = None
            self.board[row][new_rook_col] = rook
            rook.position = (row, new_rook_col)
            rook.has_moved = True
        
        # Normal move execution
        self.board[row][col] = None
        captured_piece = self.board[target_row][target_col]
        
        # Handle en passant capture
        if en_passant_capture:
            # Remove the captured pawn
            pawn_row = row  # The captured pawn is on the same row as the capturing pawn
            self.board[pawn_row][target_col] = None
        
        # Move the piece
        self.board[target_row][target_col] = piece
        piece.position = target_pos
        piece.has_moved = True
        
        # Set en passant vulnerability
        if pawn_double_move:
            piece.is_en_passant_vulnerable = True
            # Set the en passant target square
            direction = -1 if piece.color == Color.WHITE else 1
            self.en_passant_target = (row + direction, col)
        else:
            self.en_passant_target = None
        
        # Pawn promotion (to queen for simplicity)
        if piece.piece_type == PieceType.PAWN:
            if (piece.color == Color.WHITE and target_row == 0) or (piece.color == Color.BLACK and target_row == 7):
                # Promote to queen
                self.board[target_row][target_col] = Piece(PieceType.QUEEN, piece.color, (target_row, target_col))
        
        # Update game state
        self.last_move = (piece, (row, col), target_pos)
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        self.selected_piece = None
        self.valid_moves = []
        
        return True

    def handle_click(self, mouse_pos):
        # Convert mouse position to board coordinates
        col = mouse_pos[0] // SQUARE_SIZE
        row = mouse_pos[1] // SQUARE_SIZE
        
        clicked_piece = self.board[row][col] if self.is_valid_position(row, col) else None
        
        # If no piece is selected and a piece of the current turn's color is clicked, select it
        if self.selected_piece is None:
            if clicked_piece is not None and clicked_piece.color == self.current_turn:
                self.selected_piece = clicked_piece
                self.valid_moves = self.get_valid_moves(clicked_piece)
        else:
            # If a piece is already selected
            if clicked_piece is not None and clicked_piece.color == self.current_turn:
                # If clicking on another friendly piece, select it instead
                self.selected_piece = clicked_piece
                self.valid_moves = self.get_valid_moves(clicked_piece)
            else:
                # Try to move to the clicked position
                if (row, col) in self.valid_moves:
                    self.move_piece(self.selected_piece, (row, col))
                else:
                    # Deselect if clicking on an invalid position
                    self.selected_piece = None
                    self.valid_moves = []

    def draw(self, screen, piece_images):
        # Draw the board
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        
        # Highlight selected piece
        if self.selected_piece:
            row, col = self.selected_piece.position
            pygame.draw.rect(screen, HIGHLIGHT, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        
        # Draw valid move indicators
        for row, col in self.valid_moves:
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(s, MOVE_HIGHLIGHT, (SQUARE_SIZE // 2, SQUARE_SIZE // 2), SQUARE_SIZE // 6)
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
        
        # Draw pieces
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    image_key = piece.get_image_key()
                    if image_key in piece_images:
                        screen.blit(piece_images[image_key], (col * SQUARE_SIZE, row * SQUARE_SIZE))