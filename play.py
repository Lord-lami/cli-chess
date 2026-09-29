import game, chessBoard
import logging, argparse, shelve, sys
from pathlib import Path


parser = argparse.ArgumentParser(
    description="CLI Chess: Make your boring CLI more fun",
    epilog="Example: python chessBoard.py"
)
parser.add_argument(
    "-l", "--log-level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE"],
    default="NONE",
    help="Minimum log level to display (default: NONE)"
)

parser.add_argument(
    "-t", "--turn-duration",
    type=int,
    default=0,
    help="The turn duration in seconds. A value less than 1 will result in no time limit (default: 0)."
)

parser.add_argument(
    "-np", "--no-pause",
    action="store_true",
    help="Disables the pause command"
)

subparsers = parser.add_subparsers(dest="command")

load_parser = subparsers.add_parser("load")
load_parser.add_argument(
    "-f", "--filename",
    type=str,
    default="autosave",
    help="Filename of the save file in saves folder to load"
)

ARGS = parser.parse_args()

if ARGS.log_level != "NONE":
    levels = logging.getLevelNamesMapping()
    logging.basicConfig(level=levels[ARGS.log_level], format='%(asctime)s -  %(levelname)s -  %(message)s')
else:
    logging.disable()



print('CLI Chessboard')
print('by Olamide Ifarajimi')

turn_duration, pause = ARGS.turn_duration, False
remaining_time, current_player= turn_duration, "White"
board = chessBoard.STARTING_BOARD

if ARGS.no_pause:
    pause = None

Path("saves").mkdir(exist_ok=True)

if ARGS.command == "load":
    load_file = Path("saves") / Path(ARGS.filename)
    if not load_file.exists():
        print(f"There is no game save file, {load_file}", file=sys.stderr)
        sys.exit(1)
    with shelve.open(load_file) as saved_game:
        turn_duration = saved_game["turn_duration"]
        pause = saved_game["pause"]
        remaining_time = saved_game["remaining_time"]
        current_player = saved_game["current_player"]
        board = saved_game["board"]

save_filename, remaining_time, current_player, player_message, board = game.lax_game(turn_duration, pause, \
                                                                     remaining_time, current_player, \
                                                                        board)
if ARGS.command == "load" and save_filename == "autosave":
    save_filename = ARGS.filename

with shelve.open("saves/"+save_filename) as saved_game:
    saved_game["turn_duration"] = turn_duration
    saved_game["pause"] = pause
    saved_game["remaining_time"] = remaining_time
    saved_game["current_player"] = current_player
    saved_game["board"] = board
