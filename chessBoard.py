import copy, sys, logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s -  %(levelname)s -  %(message)s')
# logging.disable(logging.CRITICAL)

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
# 1. Pieces that are outside of the valid pieces: {'wP', 'wN', 'bK', 'bP', 'wR', 'bR', 'wK', 'wQ', 'bN', 'bB', 'bQ', 'wB'}
# 2. More than 16 White pieces or Black pieces
# 3. More than 8 White Pawns
# 4. More than 1 White King or Black King
def is_valid_chess_board(board: dict[str, str]) -> bool:
    valid_pieces = set(STARTING_BOARD.values())
    white_piece_count = {"P": 0, "R": 0, "N": 0, "B": 0, "Q": 0, "K": 0}
    black_piece_count = {"P": 0, "R": 0, "N": 0, "B": 0, "Q": 0, "K": 0}
    total_white_piece_count = 0
    total_black_piece_count = 0
    for _, piece in board.items():
        if piece not in valid_pieces:
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

    logging.debug("The Chess Board is Valid")
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


def is_valid_position(position: str) -> bool:
    if len(position) != 2:
        return False
    if position[0] not in COLS:
        return False
    if position[1] not in ROWS:
        return False
    
    return True

instructions = '''
Pieces:
  w - White, b - Black
  P - Pawn, N - Knight, B - Bishop, R - Rook, Q - Queen, K - King
  Example:
    wB - White Bishop
Commands:
  move e2 e4 [message] - Moves the piece at e2 to e4. You can optionally add a player message.
  remove e2 - Removes the piece at e2.
  set e2 wP - Sets square e2 to a white pawn.
  reset - Resets pieces back to their starting squares.
  clear - Clears the entire board.
  fill wP - Fills entire board with white pawns.
  quit - Quits the program.
'''

print('Interactive Chessboard')
print('by Olamide Ifarajimi')

main_board = copy.copy(STARTING_BOARD)
player_message = ""
computer_message = ""

while True:
    print(instructions)
    print_chess_board(main_board)
    if player_message:
        print("Player:", player_message)
        player_message = ""
    if computer_message:
        print("Computer:", computer_message)
        computer_message = ""
    command = input("> ")
    prompt = command.split()
    match prompt[0]:
        case "move":
            # Raise Exception if there are less than 2 positions written after move
            if len(prompt) < 3:
                computer_message = f"Invalid Move {command} : Missing Position argument(s)"
                logging.error(computer_message)
                continue

            # Anything written after the positions is a player message
            if len(prompt) > 3:
                player_message = " ".join(prompt[3:])
                logging.info("Received player message: " + player_message)
            
            # Check that the postions are valid
            if not is_valid_position(prompt[1]):
                computer_message = f"Invalid Move - {command} : Invalid Position - {prompt[1]}"
                logging.warning(computer_message)
                continue
            if not is_valid_position(prompt[2]):
                computer_message = f"Invalid Move - {command} : Invalid Position - {prompt[2]}"
                logging.warning(computer_message)
                continue
            logging.info("Positions are Valid")

            # Check that the postions have pieces on them
            if prompt[1] not in main_board.keys():
                computer_message = f"Invalid Move - {command} : No Pieces at Position - {prompt[1]}"
                logging.warning(computer_message)
                continue
            logging.info("The First Position has a piece on it")

            main_board[prompt[2]] = main_board[prompt[1]]
            del main_board[prompt[1]]

        case "remove":
            if len(prompt) != 2:
                computer_message = f"Invalid Remove - {command} : Invalid Number of arguments - {len(prompt)}"
                logging.error(computer_message)
                continue
            if prompt[1] not in main_board.keys():
                computer_message = f"Invalid Move - {command} : No Pieces at Position - {prompt[1]}"
                logging.warning(computer_message)
                continue
            del main_board[prompt[1]]
        case "set":
            if len(prompt) != 3:
                computer_message = f"Invalid Set - {command} : Invalid Number of arguments - {len(prompt)}"
                logging.error(computer_message)
                continue
            main_board[prompt[1]] = prompt[2]
        case "reset":
            if len(prompt) != 1:
                computer_message = f"Invalid Reset - {command} : Invalid Number of arguments - {len(prompt)}"
                logging.error(computer_message)
                continue
            main_board = copy.copy(STARTING_BOARD)
        case "clear":
            if len(prompt) != 1:
                computer_message = f"Invalid Clear - {command} : Invalid Number of arguments - {len(prompt)}"
                logging.error(computer_message)
                continue
            main_board = {}
        case "fill":
            if len(prompt) != 2:
                computer_message = f"Invalid Fill - {command} : Invalid Number of arguments - {len(prompt)}"
                logging.error(computer_message)
                continue
            for row in ROWS:
                for col in COLS:
                    main_board[col+row] = prompt[1]
        case "quit":
            sys.exit()
        case _:
            computer_message = f"Invalid command - {prompt[0]}"
            logging.error(computer_message)
