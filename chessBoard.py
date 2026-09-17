import copy, sys, logging, argparse
from timer import timer_timed_input

parser = argparse.ArgumentParser(
    description="CLI Chess: Make you boring CLI more fun",
    epilog="Example: python chessBoard.py"
)
parser.add_argument(
    "-l", "--log-level",
    choices=["NONE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    default="NONE",
    help="Minimum log level to display (default: NONE)"
)

parser.add_argument(
    "-d", "--duration",
    type=int,
    default=0,
    help="The turn duration in seconds. A value less than 1 will result in no time limit (default: 0)."
)

ARGS = parser.parse_args()
if ARGS.log_level != "NONE":
    levels = logging.getLevelNamesMapping()
    logging.basicConfig(level=levels[ARGS.log_level], format='%(asctime)s -  %(levelname)s -  %(message)s')
else:
    logging.disable()

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

# movePiece takes the piece at fromPos in the main_board and
# puts it at toPos in the main_board.
# It returns a computer message if:
# 1. Any of the positions are not valid
# 2. There is no piece at fromPos
def movePiece(fromPos: str, toPos: str, command: str) -> str:

    # Check that the postions are valid
    if not is_valid_position(fromPos):
        computer_message = f"Invalid Move - {command} : Invalid Position - {fromPos}"
        logging.warning(computer_message)
        return computer_message
    if not is_valid_position(toPos):
        computer_message = f"Invalid Move - {command} : Invalid Position - {toPos}"
        logging.warning(computer_message)
        return computer_message

    logging.info("Positions are Valid")

    # Check that the first postion has a piece on it
    if fromPos not in main_board.keys():
        computer_message = f"Invalid Move - {command} : No Pieces at Position - {fromPos}"
        logging.warning(computer_message)
        return computer_message

    logging.info("The First Position has a Piece on it")

    main_board[toPos] = main_board[fromPos]
    del main_board[fromPos]


# removePiece removes the piece at fromPos from the main_board
# It returns a computer_message if:
# 1. fromPos is not a valid chessboard position
# 2. There is no piece at fromPos
def removePiece(fromPos: str, command: str) -> str:

    # Check that the postion is valid
    if not is_valid_position(fromPos):
        computer_message = f"Invalid Remove - {command} : Invalid Position - {fromPos}"
        logging.warning(computer_message)
        return computer_message

    if fromPos not in main_board.keys():
        computer_message = f"Invalid Remove - {command} : No Pieces at Position - {fromPos}"
        logging.warning(computer_message)
        return computer_message

    del main_board[fromPos]

# setPiece sets the piece toPiece on the position pos on the main_board
# It returns a computer message if:
# 1. The pos is not valid chessboard position
# 2. toPiece is outside of the VALID_PIECES
def setPiece(pos: str, toPiece: str, command: str) -> str:

    # Check that the postion is valid
    if not is_valid_position(pos):
        computer_message = f"Invalid Set - {command} : Invalid Position - {pos}"
        logging.warning(computer_message)
        return computer_message

    if toPiece not in VALID_PIECES:
        computer_message = f"Invalid Set - {command} : Invalid Piece - {toPiece}"
        logging.warning(computer_message)
        return computer_message
    
    main_board[pos] = toPiece


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

main_board = copy.copy(STARTING_BOARD)
player_message = ""
computer_message = ""
current_player = "White"
next_player = "Black"
remaining_time = ARGS.duration

print('Interactive Chessboard')
print('by Olamide Ifarajimi')

while True:
    print(instructions)
    print_chess_board(main_board)

    if player_message:
        print(player_message)
        player_message = ""
    if computer_message:
        print("Computer:", computer_message)
        computer_message = ""

    if ARGS.duration < 1:
        command = input(current_player+"> ")
    else:
        command, remaining_time = timer_timed_input(remaining_time, "-"+current_player+"> ")
    
    if remaining_time == 0:
        remaining_time = ARGS.duration

    if not command:
        computer_message = f"No Command Given"
        logging.error(computer_message)
        continue

    prompt = command.split()
    match prompt[0]:
        case "move":
            # Show an error message if there are less than 2 positions written after move
            if len(prompt) < 3:
                computer_message = f"Invalid Move {command} : Missing Position argument(s)"
                logging.error(computer_message)
                continue

            # Anything written after the positions is a player message
            if len(prompt) > 3:
                player_message = " ".join(prompt[3:])
                logging.info("Received player message: " + player_message)

            computer_message = movePiece(prompt[1], prompt[2], command)
            if computer_message:
                continue

        case "remove":
            if len(prompt) != 2:
                computer_message = f"Invalid Remove - {command} : Invalid Number of arguments - {len(prompt)}"
                logging.error(computer_message)
                continue

            computer_message = removePiece(prompt[1], command)
            if computer_message:
                continue
            
        case "set":
            if len(prompt) != 3:
                computer_message = f"Invalid Set - {command} : Invalid Number of arguments - {len(prompt)}"
                logging.error(computer_message)
                continue
            computer_message = setPiece(prompt[1], prompt[2], command)
            if computer_message:
                continue
            

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
            continue

    player_message = current_player + ": " + player_message if player_message else ""
    current_player, next_player = next_player, current_player
    remaining_time = 30
