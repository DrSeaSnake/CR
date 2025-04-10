from enum import Enum

# Piece types
class PieceType(Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

# Piece colors
class Color(Enum):
    WHITE = 1
    BLACK = 2

class Piece:
    def __init__(self, piece_type, color, position):
        self.piece_type = piece_type
        self.color = color
        self.position = position
        self.has_moved = False  # For castling and pawn double move
        self.is_en_passant_vulnerable = False  # For en passant

    def get_image_key(self):
        color_letter = "w" if self.color == Color.WHITE else "b"
        piece_letter = {
            PieceType.PAWN: "p",
            PieceType.KNIGHT: "n",
            PieceType.BISHOP: "b",
            PieceType.ROOK: "r",
            PieceType.QUEEN: "q",
            PieceType.KING: "k"
        }[self.piece_type]
        return color_letter + piece_letter