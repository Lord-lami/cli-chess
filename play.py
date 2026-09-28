import game
import logging, argparse


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
    "-t", "--turn-duration",
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



print('CLI Chessboard')
print('by Olamide Ifarajimi')

game.new_game(ARGS.turn_duration)
