import chess
import chess.engine
import chess.svg
import tkinter as tk
from tkinter import Canvas, PhotoImage


class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.current_color = chess.WHITE  # Start with white's turn


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess OPP-White")

        self.chess_game = ChessGame()

        self.canvas = Canvas(self.root, width=480, height=480)
        self.canvas.pack()

        self.piece_images = self.load_piece_images()

        self.canvas.bind("<Button-1>", self.handle_click)

        self.draw_board()

    def load_piece_images(self):
        piece_images = {}
        colors = ['w', 'b']
        pieces = ['P', 'N', 'B', 'R', 'Q', 'K']

        for color in colors:
            for piece in pieces:
                filename = f"/Images/{color}{piece}.png"
                piece_images[f"{color}{piece}"] = PhotoImage(file=filename)

        return piece_images

    def handle_click(self, event):
        if self.chess_game.current_color == chess.WHITE:
            file = event.x // 60
            rank = 7 - event.y // 60

            square = chess.square(file, rank)
            square_name = chess.square_name(square)
            print("Square Chosen", square_name)
            if hasattr(self, "selected_square"):
                move = chess.Move(self.selected_square, square)
                print("Move made", move)
                if move in self.chess_game.board.legal_moves:
                    self.chess_game.board.push(move)
                    self.handle_special_cases(move)
                    self.draw_board()
                    delattr(self, "selected_square")  # Clear selected square
                    self.switch_turn()
            elif self.chess_game.board.piece_at(square) and \
                    self.chess_game.board.piece_at(square).color == self.chess_game.current_color:
                self.selected_square = square
                self.highlight_legal_moves()

        # Computer's move
        if self.chess_game.current_color == chess.BLACK:
            computer_move = self.get_computer_move(move)
            self.chess_game.board.push(computer_move)
            self.draw_board()
            self.switch_turn()

    def get_computer_move(self, other_move):

        #print(self.chess_game.board)
        with chess.engine.SimpleEngine.popen_uci(
                r"\stockfish\stockfish-windows-x86-64-avx2.exe") as engine:
            result = engine.play(self.chess_game.board, chess.engine.Limit(time=2.0))
            suggested_move = result.move
        
        print("Computer Move", suggested_move)
        #print(self.chess_game.board)
        return suggested_move

    def switch_turn(self):
        self.chess_game.current_color = not self.chess_game.current_color  # Switch turn
        print("Switching turn to", "White" if self.chess_game.current_color else "Black", end="\n\n")

    def highlight_legal_moves(self):
        self.legal_moves = [move.to_square for move in self.chess_game.board.legal_moves
                            if move.from_square == self.selected_square]
        self.draw_board()

    def handle_special_cases(self, move):
        # Handle pawn promotion
        if self.chess_game.board.piece_at(move.to_square) == chess.Piece(chess.PAWN, not self.chess_game.current_color):
            if chess.rank(move.to_square) == 0 or chess.rank(move.to_square) == 7:
                # Promote pawn to queen for simplicity, you can add a UI to choose promotion piece
                # promotion_piece = chess.QUEEN
                # self.chess_game.board.set_piece_at(move.to_square,
                # chess.Piece(promotion_piece, self.chess_game.current_color))
                print("Pawn promoted")

        # Handle check blocking
        if self.chess_game.board.is_checkmate():
            print("Checkmate!")

    def is_check_blocked(self):
        # Check if the check can be blocked by moving a piece
        for move in self.chess_game.board.legal_moves:
            if self.chess_game.board.is_checkmate():
                return True
        return False

    def draw_board(self):
        self.canvas.delete("all")

        for rank in range(8):
            for file in range(8):
                color = "#D2B48C" if (rank + file) % 2 == 0 else "#FFDAB9"
                self.canvas.create_rectangle(file * 60, (7 - rank) * 60,
                                             (file + 1) * 60, (8 - rank) * 60,
                                             fill=color)

        for square in chess.SQUARES:
            piece = self.chess_game.board.piece_at(square)
            if piece:
                color = 'w' if piece.color == chess.WHITE else 'b'
                piece_key = f"{color}{piece.symbol().upper()}"
                image = self.piece_images.get(piece_key)
                if image:
                    self.canvas.create_image((square % 8) * 60 + 30, (7 - square // 8) * 60 + 30,
                                             image=image)

        if hasattr(self, "selected_square"):
            for square in self.legal_moves:
                self.canvas.create_rectangle((square % 8) * 60, (7 - square // 8) * 60,
                                             (square % 8 + 1) * 60, (8 - square // 8) * 60,
                                             outline="blue", width=3)


if __name__ == "__main__":
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()
