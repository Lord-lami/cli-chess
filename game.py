import chessBoard, timer
import logging, copy

main_board = dict()

# movePiece takes the piece at fromPos in the main_board and
# puts it at toPos in the main_board.
# It returns a computer message if:
# 1. Any of the positions are not valid
# 2. There is no piece at fromPos
def movePiece(fromPos: str, toPos: str, command: str) -> str:
    global main_board
    # Check that the postions are valid
    if not chessBoard.is_valid_position(fromPos):
        computer_message = f"Invalid Move - {command} : Invalid Position - {fromPos}"
        logging.warning(computer_message)
        return computer_message
    if not chessBoard.is_valid_position(toPos):
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
    global main_board
    # Check that the postion is valid
    if not chessBoard.is_valid_position(fromPos):
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
    global main_board
    # Check that the postion is valid
    if not chessBoard.is_valid_position(pos):
        computer_message = f"Invalid Set - {command} : Invalid Position - {pos}"
        logging.warning(computer_message)
        return computer_message

    if toPiece not in chessBoard.VALID_PIECES:
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
  pause - Pauses the game if pausing is not disabled.
  help - Displays this text.
  quit - Quits the program.
'''
def new_game(turn_duration: int, noPause: bool) -> tuple[int, str, dict]:
    global main_board
    main_board = copy.copy(chessBoard.STARTING_BOARD)
    advice = "Use the 'help' command to view the instructions"
    paused = False
    player_message = ""
    computer_message = ""
    current_player = "White"
    next_player = "Black"
    remaining_time = turn_duration

    print(instructions)
    chessBoard.print_chess_board(main_board)

    while True:
        if paused:
            print("Press Enter to continue", end="")
            input()
            paused = False

        if player_message:
            print(player_message)
            player_message = ""
        if computer_message:
            print("Computer:", computer_message)
            computer_message = ""

        if turn_duration < 1:
            command = input(current_player+"> ")
        else:
            command, remaining_time = timer.timer_timed_input(remaining_time, "-"+current_player+"> ")
        
        if turn_duration > 0 and remaining_time == 0:
            computer_message = f"Turn Expired"
            logging.error(computer_message)
            computer_message += "\n" + advice
            # The next code line should be replaced with losing logic 
            # for the current player when implementing chess rules
            remaining_time = turn_duration
            continue

        if not command:
            computer_message = "No Command Given"
            logging.error(computer_message)
            computer_message += "\n" + advice
            continue

        prompt = command.split()
        match prompt[0]:
            case "move":
                # Show an error message if there are less than 2 positions written after move
                if len(prompt) < 3:
                    computer_message = f"Invalid Move {command} : Missing Position argument(s)"
                    logging.error(computer_message)
                    computer_message += "\n" + advice
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
                    computer_message += "\n" + advice
                    continue

                computer_message = removePiece(prompt[1], command)
                if computer_message:
                    continue
                
            case "set":
                if len(prompt) != 3:
                    computer_message = f"Invalid Set - {command} : Invalid Number of arguments - {len(prompt)}"
                    logging.error(computer_message)
                    computer_message += "\n" + advice
                    continue
                computer_message = setPiece(prompt[1], prompt[2], command)
                if computer_message:
                    continue
                

            case "reset":
                if len(prompt) != 1:
                    computer_message = f"Invalid Reset - {command} : Invalid Number of arguments - {len(prompt)}"
                    logging.error(computer_message)
                    computer_message += "\n" + advice
                    continue

                main_board = copy.copy(chessBoard.STARTING_BOARD)

            case "clear":
                if len(prompt) != 1:
                    computer_message = f"Invalid Clear - {command} : Invalid Number of arguments - {len(prompt)}"
                    logging.error(computer_message)
                    computer_message += "\n" + advice
                    continue

                main_board = {}

            case "fill":
                if len(prompt) != 2:
                    computer_message = f"Invalid Fill - {command} : Invalid Number of arguments - {len(prompt)}"
                    logging.error(computer_message)
                    computer_message += "\n" + advice
                    continue

                for row in chessBoard.ROWS:
                    for col in chessBoard.COLS:
                        main_board[col+row] = prompt[1]

            case "pause":
                if not noPause:
                    paused = True
                    continue
                else:
                    computer_message = "Cannot Pause, Pausing is disabled"
                    logging.info(computer_message)
                    continue

            case "help":
                print(instructions)
                continue
            
            case "quit":
                return remaining_time, current_player, main_board

            case _:
                computer_message = f"Invalid command - {prompt[0]}"
                logging.error(computer_message)
                computer_message += "\n" + advice
                continue

        player_message = current_player + ": " + player_message if player_message else ""
        current_player, next_player = next_player, current_player
        remaining_time = turn_duration
        chessBoard.print_chess_board(main_board)
