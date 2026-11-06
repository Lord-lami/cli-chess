import chessBoard, timer, gamePlay, possibleMoves
import logging, copy



def play(turn_duration: int, noPause: bool|None, arbiter: bool, remaining_time: int, current_player: str, board: dict[str, str]) -> tuple[str, int, str, dict]:
    """An offline game of CLI Chess"""
    gamePlay.main_board = board
    computer_message = ""
    player_message = ""

    next_player = "Black"
    if current_player == "Black":
        next_player = "White"
    
    print(gamePlay.INSTRUCTIONS)
    chessBoard.print_chess_board(gamePlay.main_board)

    while True:
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
            computer_message += "\n" + gamePlay.ADVICE
            # The next code line should be replaced with losing logic 
            # for the current player when implementing chess rules
            remaining_time = turn_duration
            continue

        if not command:
            computer_message = "No Command Given"
            logging.error(computer_message)
            computer_message += "\n" + gamePlay.ADVICE
            continue

        prompt = command.split()
        match prompt[0]:
            case "move":
                # Show an error message if there are less than 2 positions written after move
                if len(prompt) < 3:
                    computer_message = f"Invalid Move {command} : Missing Position argument(s)"
                    logging.error(computer_message)
                    computer_message += "\n" + gamePlay.ADVICE
                    continue

                # Anything written after the positions is a player message
                if len(prompt) > 3:
                    player_message = " ".join(prompt[3:])
                    logging.info("Received player message: " + player_message)

                computer_message = gamePlay.movePiece(prompt[1], prompt[2], command, arbiter)
                if computer_message:
                    continue

            case "remove":
                if len(prompt) != 2:
                    computer_message = f"Invalid Remove - {command} : Invalid Number of arguments - {len(prompt)}"
                    logging.error(computer_message)
                    computer_message += "\n" + gamePlay.ADVICE
                    continue

                computer_message = gamePlay.removePiece(prompt[1], command)
                if computer_message:
                    continue
                
            case "set":
                if len(prompt) != 3:
                    computer_message = f"Invalid Set - {command} : Invalid Number of arguments - {len(prompt)}"
                    logging.error(computer_message)
                    computer_message += "\n" + gamePlay.ADVICE
                    continue
                computer_message = gamePlay.setPiece(prompt[1], prompt[2], command)
                if computer_message:
                    continue
                

            case "reset":
                if len(prompt) != 1:
                    computer_message = f"Invalid Reset - {command} : Invalid Number of arguments - {len(prompt)}"
                    logging.error(computer_message)
                    computer_message += "\n" + gamePlay.ADVICE
                    continue

                gamePlay.main_board = copy.copy(chessBoard.STARTING_BOARD)

            case "clear":
                if len(prompt) != 1:
                    computer_message = f"Invalid Clear - {command} : Invalid Number of arguments - {len(prompt)}"
                    logging.error(computer_message)
                    computer_message += "\n" + gamePlay.ADVICE
                    continue

                gamePlay.main_board = {}

            case "fill":
                if len(prompt) != 2:
                    computer_message = f"Invalid Fill - {command} : Invalid Number of arguments - {len(prompt)}"
                    logging.error(computer_message)
                    computer_message += "\n" + gamePlay.ADVICE
                    continue

                for row in chessBoard.ROWS:
                    for col in chessBoard.COLS:
                        gamePlay.main_board[col+row] = prompt[1]
            case "legal":
                if len(prompt) != 2:
                    computer_message = f"Invalid Legal - {command} : Invalid Number of arguments - {len(prompt)}"
                    logging.error(computer_message)
                    computer_message += "\n" + gamePlay.ADVICE
                    continue

                legal_moves = possibleMoves.legal_moves(gamePlay.main_board, prompt[1])
                protoboard = gamePlay.main_board.copy()
                piece = protoboard[prompt[1]]
                del protoboard[prompt[1]]
                for move in legal_moves:
                    protoboard[move] = piece
                computer_message = f"Legal Moves: {legal_moves}"
                chessBoard.print_chess_board(protoboard)
                continue

            case "pause":
                if noPause != None:
                    print("Press Enter to continue", end="")
                    input()
                    continue
                else:
                    computer_message = "Cannot Pause: Pausing is disabled"
                    logging.info(computer_message)
                    continue

            case "help":
                print(gamePlay.INSTRUCTIONS)
                continue
            
            case "quit":
                save_filename = "autosave"
                if len(prompt) > 1:
                    save_filename = prompt[1]
                return save_filename, remaining_time, current_player, gamePlay.main_board

            case _:
                from_pos, to_pos = possibleMoves.get_move_positions(current_player[0].lower(), command, gamePlay.main_board)
                if from_pos and to_pos:
                    gamePlay.main_board[to_pos] = gamePlay.main_board[from_pos]
                    del gamePlay.main_board[from_pos]
                else:
                    computer_message = f"Invalid command - {prompt[0]}"
                    logging.error(computer_message)
                    computer_message += "\n" + gamePlay.ADVICE
                    continue

        player_message = current_player + ": " + player_message if player_message else ""
        current_player, next_player = next_player, current_player
        remaining_time = turn_duration
        chessBoard.print_chess_board(gamePlay.main_board)

