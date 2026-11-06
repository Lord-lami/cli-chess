import chessBoard, timer, gamePlay, possibleMoves
import logging, copy, subprocess, os, sys, socket, time



def play(turn_duration: int, 
                noPause: bool|None, 
                arbiter: bool, 
                remaining_time: int, 
                current_player: str, 
                board: dict[str, str]) -> tuple[str, int, str, dict]:
    """An online game of CLI Chess"""
    read_fd, write_fd = os.pipe()

    os.environ["DATA_FD"] = str(write_fd)

    try:
        subprocess.run(["go", "run", "connect.go"], 
                       pass_fds=(write_fd,), 
                       check=True, 
                       stderr=sys.stderr)

        # play no longer needs its own copy of the write end.
        os.close(write_fd)
        write_fd = -1

        # Read data from connect.go.
        with os.fdopen(read_fd, "r") as pipe:
            read_fd = -1
            data = pipe.read()

        print("Received from connect.go:", data)

    finally:
        if write_fd != -1:
            os.close(write_fd)

        if read_fd != -1:
            os.close(read_fd)

    print("Opponent Socket:", data)

    piece_color = data[-1]
    socket_str = data[:-1]
    oppAddr, myAddr = socket_str.rsplit(",", 1)
    host, port = myAddr.rsplit(":", 1)
    oppHost, oppPort = oppAddr.rsplit(":", 1)

    white_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    white_soc.bind((host, int(port)))

    if piece_color == "w":
        piece_color = "White"
        # Wait a bit for black to set up its TCP server
        time.sleep(1)
        white_soc.connect((oppHost, int(oppPort)))
        mySoc = white_soc
        print(white_soc.getsockname(), "vs." ,oppAddr)
    else:
        piece_color = "Black"
        white_soc.listen()
        black_soc, raddr = white_soc.accept()
        mySoc = black_soc
        print(black_soc.getsockname(), "vs.", raddr)
        # Wait for opponent to play round and send their move
    
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

        command = ""

        if piece_color == current_player:
            if turn_duration < 1:
                command = input(current_player+"> ")
            else:
                command, remaining_time = timer.timer_timed_input(remaining_time, "-"+current_player+"> ")
        else:
            if turn_duration < 1:
                print(f"Waiting for {current_player}'s move...")
                command = mySoc.recv(1024).decode(encoding="utf-8")
                if not command:
                    print("The connection has been closed")
                    return
            else:
                print(f"Waiting for {current_player}'s move in {turn_duration} seconds")
                data = mySoc.recv(1024).decode(encoding="utf-8")
                if not data:
                    print("The connection has been closed")
                    return
                command, remaining_time = data.rsplit("|", 1)
                remaining_time = int(remaining_time)
                
        
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
                if piece_color == "Black":
                    black_soc.close()
                white_soc.close()
                return save_filename, remaining_time, current_player, gamePlay.main_board

            case _:
                computer_message = f"Invalid command - {prompt[0]}"
                logging.error(computer_message)
                computer_message += "\n" + gamePlay.ADVICE
                continue

        # Only send your own moves
        if current_player == piece_color:
            packet = command
            if turn_duration > 1:
                packet += "|" + str(remaining_time)
            mySoc.send(packet.encode("utf-8"))
        player_message = current_player + ": " + player_message if player_message else ""
        current_player, next_player = next_player, current_player
        remaining_time = turn_duration
        chessBoard.print_chess_board(gamePlay.main_board)

