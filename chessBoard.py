import copy, logging

starting_board = {}
ROWS = "87654321"
COLS = "abcdefgh"

# Fill the starting_board dictionary with 
# the - starting_board[position] = piece - format
# of a starting chessboard
for letter in COLS:
    starting_board[letter+"2"] = "wP"
    starting_board[letter+"7"] = "bP"
    match letter:
        case "a" | "h":
            starting_board[letter+"1"] = "wR"
            starting_board[letter+"8"] = "bR"
        case "b" | "g":
            starting_board[letter+"1"] = "wN"
            starting_board[letter+"8"] = "bN"
        case "c" | "f":
            starting_board[letter+"1"] = "wB"
            starting_board[letter+"8"] = "bB"
        case "d":
            starting_board[letter+"1"] = "wQ"
            starting_board[letter+"8"] = "bQ"
        case "e":
            starting_board[letter+"1"] = "wK"
            starting_board[letter+"8"] = "bK"

logging.debug(starting_board)
"""STARTING_BOARD is the board at the start of a chess game.
It looks like this when printed

    a    b    c    d    e    f    g    h
   ____ ____ ____ ____ ____ ____ ____ ____
  ||||||    ||||||    ||||||    ||||||    |
8 ||bR|| bN ||bB|| bQ ||bK|| bB ||bN|| bR |
  ||||||____||||||____||||||____||||||____|
  |    ||||||    ||||||    ||||||    ||||||
7 | bP ||bP|| bP ||bP|| bP ||bP|| bP ||bP||
  |____||||||____||||||____||||||____||||||
  ||||||    ||||||    ||||||    ||||||    |
6 ||||||    ||||||    ||||||    ||||||    |
  ||||||____||||||____||||||____||||||____|
  |    ||||||    ||||||    ||||||    ||||||
5 |    ||||||    ||||||    ||||||    ||||||
  |____||||||____||||||____||||||____||||||
  ||||||    ||||||    ||||||    ||||||    |
4 ||||||    ||||||    ||||||    ||||||    |
  ||||||____||||||____||||||____||||||____|
  |    ||||||    ||||||    ||||||    ||||||
3 |    ||||||    ||||||    ||||||    ||||||
  |____||||||____||||||____||||||____||||||
  ||||||    ||||||    ||||||    ||||||    |
2 ||wP|| wP ||wP|| wP ||wP|| wP ||wP|| wP |
  ||||||____||||||____||||||____||||||____|
  |    ||||||    ||||||    ||||||    ||||||
1 | wR ||wN|| wB ||wQ|| wK ||wB|| wN ||wR||
  |____||||||____||||||____||||||____||||||


"""
STARTING_BOARD = copy.copy(starting_board)
del starting_board

# The {}s are to be replaced with pieces, pipes(||) or spaces(  )
BOARD_TEMPLATE = """
    a    b    c    d    e    f    g    h
   ____ ____ ____ ____ ____ ____ ____ ____
  ||||||    ||||||    ||||||    ||||||    |
8 ||{}|| {} ||{}|| {} ||{}|| {} ||{}|| {} |
  ||||||____||||||____||||||____||||||____|
  |    ||||||    ||||||    ||||||    ||||||
7 | {} ||{}|| {} ||{}|| {} ||{}|| {} ||{}||
  |____||||||____||||||____||||||____||||||
  ||||||    ||||||    ||||||    ||||||    |
6 ||{}|| {} ||{}|| {} ||{}|| {} ||{}|| {} |
  ||||||____||||||____||||||____||||||____|
  |    ||||||    ||||||    ||||||    ||||||
5 | {} ||{}|| {} ||{}|| {} ||{}|| {} ||{}||
  |____||||||____||||||____||||||____||||||
  ||||||    ||||||    ||||||    ||||||    |
4 ||{}|| {} ||{}|| {} ||{}|| {} ||{}|| {} |
  ||||||____||||||____||||||____||||||____|
  |    ||||||    ||||||    ||||||    ||||||
3 | {} ||{}|| {} ||{}|| {} ||{}|| {} ||{}||
  |____||||||____||||||____||||||____||||||
  ||||||    ||||||    ||||||    ||||||    |
2 ||{}|| {} ||{}|| {} ||{}|| {} ||{}|| {} |
  ||||||____||||||____||||||____||||||____|
  |    ||||||    ||||||    ||||||    ||||||
1 | {} ||{}|| {} ||{}|| {} ||{}|| {} ||{}||
  |____||||||____||||||____||||||____||||||
"""

# is_valid_chess_board takes a board (a dict[position] = pieces) and 
# returns True if it is a valid chess board and False if it isn't
# An invalid board has:
# 1. Pieces that are outside of the VALID_PIECES
# 2. More than 16 White pieces or Black pieces
# 3. More than 8 White Pawns
# 4. More than 1 White King or Black King
VALID_PIECES = {'wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK'}
def is_valid_chess_board(board: dict[str, str]) -> bool:
    white_piece_count = {"P": 0, "R": 0, "N": 0, "B": 0, "Q": 0, "K": 0}
    black_piece_count = {"P": 0, "R": 0, "N": 0, "B": 0, "Q": 0, "K": 0}
    total_white_piece_count = 0
    total_black_piece_count = 0
    for _, piece in board.items():
        if piece not in VALID_PIECES:
            logging.info("Invalid Chess Board: Invalid Piece - "+ piece)
            return False
        
        if piece[0] == "w":
            white_piece_count[piece[1]] += 1
            total_white_piece_count += 1
        else:
            black_piece_count[piece[1]] += 1
            total_black_piece_count += 1
        
    if white_piece_count["P"] > 8:
        logging.info(f"Invalid Chess Board: Too many White Pawns - {white_piece_count["P"]}")
        return False
    if black_piece_count["P"] > 8:
        logging.info(f"Invalid Chess Board: Too many Black Pawns - {black_piece_count["P"]}")
        return False
    if white_piece_count["K"] > 1:
        logging.info(f"Invalid Chess Board: More than 1 White King - {white_piece_count["K"]}")
        return False
    if black_piece_count["K"] > 1:
        logging.info(f"Invalid Chess Board: More than 1 Black King - {black_piece_count["K"]}")
        return False
    if total_white_piece_count > 16:
        logging.info(f"Invalid Chess Board: Too Many White Pieces - {total_white_piece_count}")
        return False
    if total_black_piece_count > 16:
        logging.info(f"Invalid Chess Board: Too Many Black Pieces - {total_black_piece_count}")
        return False

    logging.info("The Chess Board is Valid")
    return True

WHITE_SQUARE = '||'
BLACK_SQUARE = '  '

# print_chess_board takes a board and prints the chess board to a terminal
def print_chess_board(board: dict[str, str]) -> None:
    is_valid_chess_board(board)
    b_temp = copy.copy(BOARD_TEMPLATE)

    row = 0
    col = 0
    current_ind = b_temp.find("{}", 0)
    is_white_tile = True
    while current_ind != -1:
        position = COLS[col] + ROWS[row]
        if position in board.keys():
            b_temp = b_temp[:current_ind] + board[position] + b_temp[current_ind+2:]
        else:
            if is_white_tile:
                b_temp = b_temp[:current_ind] + WHITE_SQUARE + b_temp[current_ind+2:]
            else:
                b_temp = b_temp[:current_ind] + BLACK_SQUARE + b_temp[current_ind+2:]

        if col < 7:
            col += 1
        else:
            col = 0
            row += 1
            is_white_tile = not is_white_tile
        is_white_tile = not is_white_tile
        current_ind = b_temp.find("{}", current_ind)
    print(b_temp)

# is_valid_position returns True if the passed position can be found on a chessboard
# and false otherwise
def is_valid_position(position: str) -> bool:
    if len(position) != 2:
        return False
    if position[0] not in COLS:
        return False
    if position[1] not in ROWS:
        return False
    
    return True
