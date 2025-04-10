import chess
import chess.engine
import os
from pieces import PieceType, Color
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChessAI")

class ChessAI:
    def __init__(self, difficulty=1, max_time=0.5):
        """
        Initialize the chess AI with a specified difficulty level.
        difficulty: 1-10, where 1 is easiest and 10 is hardest
        max_time: maximum thinking time in seconds (default: 0.5 seconds)
        """
        logger.info("Initializing ChessAI...")
        
        # Try to find the Stockfish executable
        stockfish_path = self._find_stockfish()
        if not stockfish_path:
            logger.error("Stockfish not found!")
            raise Exception("Stockfish not found. Please install Stockfish and make sure it's in your PATH or game directory.")
        
        logger.info(f"Found Stockfish at: {stockfish_path}")
        
        # Start the engine
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
            logger.info("Stockfish engine started successfully")
        except Exception as e:
            logger.error(f"Failed to start Stockfish engine: {e}")
            raise
        
        # Set difficulty (time limit and depth)
        self.difficulty = difficulty
        self.max_time = max_time  # Maximum thinking time in seconds
        self._set_difficulty(difficulty)
        logger.info(f"Difficulty set to {difficulty}, max time: {self.max_time} seconds")
        
        # Track the last seen board state to detect changes
        self.last_board_fen = None
    
    def _find_stockfish(self):
        """Try to find the Stockfish executable on various common paths"""
        logger.info("Searching for Stockfish...")
        import os
        
        # First check in the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Checking current directory: {current_dir}")
        
        # Check for common names in current directory
        stockfish_names = ["stockfish", "stockfish.exe"]
        for name in stockfish_names:
            local_path = os.path.join(current_dir, name)
            logger.info(f"Checking for {local_path}")
            if os.path.isfile(local_path):
                if os.name != 'nt':  # For non-Windows systems, check if executable
                    if os.access(local_path, os.X_OK):
                        return local_path
                else:  # On Windows, just check if the file exists
                    return local_path
        
        # Check if it's in PATH
        for name in stockfish_names:
            path = self._which(name)
            if path:
                return path
        
        # Common installation paths
        common_paths = [
            "/usr/local/bin/stockfish",
            "/usr/bin/stockfish",
            "C:/Program Files/Stockfish/stockfish.exe",
            "C:/Program Files (x86)/Stockfish/stockfish.exe",
        ]
        
        for path in common_paths:
            if os.path.isfile(path):
                return path
                
        return None
    
    def _which(self, program):
        """Check if a program is in PATH and return its full path"""
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, _ = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file
        return None
    
    def _set_difficulty(self, difficulty):
        """Set the difficulty of the engine based on the difficulty level"""
        # Scale difficulty to reasonable values
        # Difficulty 1: very quick decisions, shallow search
        # Difficulty 10: takes its time, deep search
        self.time_limit = min(self.max_time, difficulty * 0.05)  # 0.05 to 0.5 seconds max
        self.depth_limit = difficulty + 1  # Depth 2 to 11
        
        # For very low difficulties, limit the engine further or add randomness
        if difficulty <= 3:
            # Limit the engine's skill level (Stockfish-specific)
            try:
                self.engine.configure({"Skill Level": difficulty * 5})
                logger.info(f"Set Stockfish skill level to {difficulty * 5}")
            except Exception as e:
                logger.warning(f"Could not set Stockfish skill level: {e}")
    
    def convert_board_to_fen(self, chess_board):
        """
        Convert our custom chess board representation to FEN notation
        that can be understood by the python-chess library
        """
        logger.info("Converting board to FEN")
        fen_rows = []
        
        # In FEN, we go row by row from top to bottom (8 to 1 in chess notation)
        # In our board, row 0 is the top (black's side) and row 7 is the bottom (white's side)
        # So we proceed from row 0 to row 7
        for row in range(8):
            empty_count = 0
            fen_row = ""
            
            for col in range(8):
                # Get the piece at this position
                piece = chess_board.board[row][col]
                
                if piece is None:
                    empty_count += 1
                else:
                    # If there were empty squares before this piece, add them
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    
                    # Map our piece types to FEN characters
                    piece_char = self._get_fen_char(piece.piece_type)
                    
                    # Adjust case based on color
                    if piece.color == Color.WHITE:
                        fen_row += piece_char.upper()
                    else:
                        fen_row += piece_char.lower()
            
            # If there are empty squares at the end of the row
            if empty_count > 0:
                fen_row += str(empty_count)
            
            fen_rows.append(fen_row)
        
        # Join rows with slashes
        fen_position = "/".join(fen_rows)
        
        # Add active color, castling availability, etc.
        turn = "w" if chess_board.current_turn == Color.WHITE else "b"
        
        # Determine castling rights
        castling = ""
        # White kingside
        if (chess_board.board[7][4] is not None and 
            chess_board.board[7][4].piece_type == PieceType.KING and 
            chess_board.board[7][4].color == Color.WHITE and 
            not chess_board.board[7][4].has_moved and
            chess_board.board[7][7] is not None and
            chess_board.board[7][7].piece_type == PieceType.ROOK and
            chess_board.board[7][7].color == Color.WHITE and
            not chess_board.board[7][7].has_moved):
            castling += "K"
        
        # White queenside
        if (chess_board.board[7][4] is not None and 
            chess_board.board[7][4].piece_type == PieceType.KING and 
            chess_board.board[7][4].color == Color.WHITE and 
            not chess_board.board[7][4].has_moved and
            chess_board.board[7][0] is not None and
            chess_board.board[7][0].piece_type == PieceType.ROOK and
            chess_board.board[7][0].color == Color.WHITE and
            not chess_board.board[7][0].has_moved):
            castling += "Q"
        
        # Black kingside
        if (chess_board.board[0][4] is not None and 
            chess_board.board[0][4].piece_type == PieceType.KING and 
            chess_board.board[0][4].color == Color.BLACK and 
            not chess_board.board[0][4].has_moved and
            chess_board.board[0][7] is not None and
            chess_board.board[0][7].piece_type == PieceType.ROOK and
            chess_board.board[0][7].color == Color.BLACK and
            not chess_board.board[0][7].has_moved):
            castling += "k"
        
        # Black queenside
        if (chess_board.board[0][4] is not None and 
            chess_board.board[0][4].piece_type == PieceType.KING and 
            chess_board.board[0][4].color == Color.BLACK and 
            not chess_board.board[0][4].has_moved and
            chess_board.board[0][0] is not None and
            chess_board.board[0][0].piece_type == PieceType.ROOK and
            chess_board.board[0][0].color == Color.BLACK and
            not chess_board.board[0][0].has_moved):
            castling += "q"
        
        if not castling:
            castling = "-"
        
        # En passant target square
        en_passant = "-"
        if chess_board.en_passant_target:
            row, col = chess_board.en_passant_target
            file_letter = chr(col + ord('a'))
            rank_number = 8 - row
            en_passant = f"{file_letter}{rank_number}"
        
        # Halfmove clock and fullmove number - simplified for now
        halfmove_clock = "0"
        fullmove_number = "1"
        
        fen = f"{fen_position} {turn} {castling} {en_passant} {halfmove_clock} {fullmove_number}"
        
        # Check if the board state has changed
        if fen != self.last_board_fen:
            logger.info(f"New board state detected. Generated FEN: {fen}")
            self.last_board_fen = fen
        else:
            logger.warning(f"Board state hasn't changed! FEN: {fen}")
        
        return fen
    
    def _get_fen_char(self, piece_type):
        """Convert our piece type to FEN character"""
        mapping = {
            PieceType.PAWN: "p",
            PieceType.KNIGHT: "n",
            PieceType.BISHOP: "b",
            PieceType.ROOK: "r",
            PieceType.QUEEN: "q",
            PieceType.KING: "k"
        }
        return mapping.get(piece_type, "p")
    
    def get_best_move(self, chess_board):
        """
        Get the best move for the current position according to the engine.
        Returns a tuple of (piece, (to_row, to_col))
        """
        logger.info("Getting best move from Stockfish")
        
        # Log the current board state for debugging
        self._log_board_state(chess_board)
        
        # Convert our board to a python-chess board
        try:
            fen = self.convert_board_to_fen(chess_board)
            board = chess.Board(fen)
            logger.info(f"Created python-chess board from FEN: {fen}")
        except Exception as e:
            logger.error(f"Error creating python-chess board: {e}")
            raise
        
        # Let the engine think
        try:
            logger.info(f"Asking engine to think (time: {self.time_limit}s, depth: {self.depth_limit})")
            result = self.engine.play(
                board, 
                chess.engine.Limit(time=self.time_limit, depth=self.depth_limit)
            )
            logger.info(f"Engine returned move: {result.move}")
        except Exception as e:
            logger.error(f"Error getting move from engine: {e}")
            raise
        
        # Convert the move from UCI notation (e.g., "d7d5")
        move = result.move
        
        # Get the move in algebraic notation
        from_square = move.from_square
        to_square = move.to_square
        
        # In python-chess:
        # - a1 is square 0 (bottom-left)
        # - h8 is square 63 (top-right)
        # - Row goes from 0 (bottom) to 7 (top)
        # - Column goes from 0 (left) to 7 (right)
        
        # In our board:
        # - (0,0) is top-left
        # - (7,7) is bottom-right
        # - Row goes from 0 (top) to 7 (bottom)
        # - Column goes from 0 (left) to 7 (right)
        
        # Convert from python-chess coordinates to our board coordinates
        from_row = 7 - (from_square // 8)
        from_col = from_square % 8
        to_row = 7 - (to_square // 8)
        to_col = to_square % 8
        
        logger.info(f"UCI Move: {move}, From: {from_square}, To: {to_square}")
        logger.info(f"Converted move: from ({from_row}, {from_col}) to ({to_row}, {to_col})")
        
        # Find the piece at the from_square
        piece = chess_board.board[from_row][from_col]
        
        if piece is None:
            logger.error(f"No piece found at position ({from_row}, {from_col})")
            raise Exception(f"No piece found at position ({from_row}, {from_col})")
        
        logger.info(f"Found piece: {piece.piece_type.name} at ({from_row}, {from_col})")
        return piece, (to_row, to_col)
    
    def _log_board_state(self, chess_board):
        """Log the current state of the board for debugging purposes"""
        board_str = "\n"
        for r in range(8):
            for c in range(8):
                piece = chess_board.board[r][c]
                if piece is None:
                    board_str += ". "
                else:
                    symbol = self._get_fen_char(piece.piece_type)
                    if piece.color == Color.WHITE:
                        board_str += symbol.upper() + " "
                    else:
                        board_str += symbol.lower() + " "
            board_str += f" {r}\n"
        board_str += "0 1 2 3 4 5 6 7"
        logger.info(f"Current board state:\n{board_str}")
        logger.info(f"Current turn: {'WHITE' if chess_board.current_turn == Color.WHITE else 'BLACK'}")
    
    def close(self):
        """Properly close the engine when done"""
        if hasattr(self, 'engine'):
            logger.info("Closing Stockfish engine")
            self.engine.quit()