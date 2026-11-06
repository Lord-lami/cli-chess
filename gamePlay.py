import chessBoard, timer, possibleMoves
import logging, copy, subprocess, os, sys, socket, time

main_board = dict()

def movePiece(fromPos: str, toPos: str, command: str, arbiter: bool) -> str:
    """movePiece takes the piece at fromPos in the main_board and
puts it at toPos in the main_board.

It returns a computer message if:
1. Any of the positions are not valid
2. There is no piece at fromPos"""
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


    # If arbiter is set, check that the move is a legal chess move
    if arbiter:
        legal_moves = possibleMoves.legal_moves(main_board, fromPos)
        if toPos not in legal_moves:
            computer_message = "Arbiter: Illegal Move"
            return computer_message

    main_board[toPos] = main_board[fromPos]
    del main_board[fromPos]


def removePiece(fromPos: str, command: str) -> str:
    """removePiece removes the piece at fromPos from the main_board

It returns a computer_message if:
1. fromPos is not a valid chessboard position
2. There is no piece at fromPos"""
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

def setPiece(pos: str, toPiece: str, command: str) -> str:
    """setPiece sets the piece toPiece on the position pos on the main_board

It returns a computer message if:
1. The pos is not valid chessboard position
2. toPiece is outside of the VALID_PIECES"""
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


INSTRUCTIONS = '''
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
  legal e2 - Shows the legal moves available for the piece on a board and in a message
  pause - Pauses the game if pausing is not disabled with the -np flag.
  help - Displays this text.
  quit [save filename] - Quits the program and saves to the loaded save file or autosave. You can optionally add a save filename if you want to save to different file.
'''

ADVICE = "Use the 'help' command to view the instructions"
