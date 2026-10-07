# def possible_moves(board: dict[str]str) -> dict[str]list[str]:
#     pass

def parse_algebraic_move(move: str, board: dict[str, str]) -> tuple[str]:
    movelen = len(move)
    if movelen == 2:
        file = move[0]


# VALID_PIECES = {
#     'wP', 'wR', 'wN', 'wB', 'wQ', 'wK',
#     'bP', 'bR', 'bN', 'bB', 'bQ', 'bK'
# }


def get_move_positions(move, board):
    """
    Return (from_position, to_position) for an algebraic chess move.

    board: dictionary mapping positions such as 'e4' to pieces such as 'wP'.
    move: algebraic notation such as 'Nf3' or 'Bxc4'.

    Example:
        board = {
            'e2': 'wP',
            'g1': 'wK',
            'b1': 'wN'
        }

        get_move_positions('Nf3', board)
        -> ('b1', 'f3')
    """
    to_pos = move[-2:]  # e.g. 'f3'
    piece_letter = move[0]

    # Pawn move: e4, exd5, etc.
    if piece_letter in 'abcdefgh':
        piece_type = 'P'
    else:
        piece_type = piece_letter

    # Find pieces of the appropriate type.
    candidates = []

    for position, piece in board.items():
        if piece[1] == piece_type:
            candidates.append(position)

    # TODO: determine which candidate can legally reach to_pos
    

    if len(candidates) == 1:
        return candidates[0], to_pos

    raise ValueError(f"Could not uniquely determine source square for {move}")


# VALID_PIECES = {
#     'wP', 'wR', 'wN', 'wB', 'wQ', 'wK',
#     'bP', 'bR', 'bN', 'bB', 'bQ', 'bK'
# }

FILES = "abcdefgh"
RANKS = "12345678"


def legal_moves(board: dict[str, str], position: str) -> set[str]:
    """
    Return a set of positions to which the piece at `position`
    can legally move.

    board: dict[str, str]
        Maps positions such as "e4" to pieces such as "wP".

    position: str
        Position occupied by the piece to move.

    Returns:
        set[str]
    """

    color = board[position][0]
    piece = board[position][1]

    moves = set()

    if piece == 'P':
        moves |= pawn_moves(board, position, color)
    elif piece == 'N':
        moves |= knight_moves(board, position, color)
    elif piece == 'B':
        moves |= sliding_moves(
            board, position, color,
            [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        )
    elif piece == 'R':
        moves |= sliding_moves(
            board, position, color,
            [(1, 0), (-1, 0), (0, 1), (0, -1)]
        )
    elif piece == 'Q':
        moves |= sliding_moves(
            board, position, color,
            [
                (1, 1), (1, -1), (-1, 1), (-1, -1),
                (1, 0), (-1, 0), (0, 1), (0, -1)
            ]
        )
    elif piece == 'K':
        moves |= king_moves(board, position, color)

    # A move is only legal if it doesn't leave our king in check.
    legal = set()

    for destination in moves:
        new_board = board.copy()
        del new_board[position]
        new_board[destination] = color + piece

        if not in_check(new_board, color):
            legal.add(destination)

    return legal


def coords(position: str) -> tuple[int]:
    """Convert 'e4' -> (4, 3)."""
    return FILES.index(position[0]), RANKS.index(position[1])


def position(x, y: int) -> str:
    """Convert (4, 3) -> 'e4'."""
    return FILES[x] + RANKS[y]


def on_board(x, y: int) -> bool:
    """Returns true if the coordinate is a valid chess board coordinate."""
    return 0 <= x < 8 and 0 <= y < 8


def pawn_moves(board: dict[str, str], pos: str, color: str) -> set[str]:
    """Returns a the set of legal moves for a Pawn of color color, from position pos, on board board"""
    x, y = coords(pos)
    direction = 1 if color == 'w' else -1
    start_rank = 1 if color == 'w' else 6

    moves = set()

    # One square forward
    nx, ny = x, y + direction
    if on_board(nx, ny) and position(nx, ny) not in board:
        moves.add(position(nx, ny))

        # Two squares forward from starting rank
        ny2 = y + 2 * direction
        if y == start_rank and position(nx, ny2) not in board:
            moves.add(position(nx, ny2))

    # Captures
    for dx in (-1, 1):
        nx, ny = x + dx, y + direction

        if not on_board(nx, ny):
            continue

        target = position(nx, ny)

        if target in board and board[target][0] != color:
            moves.add(target)

    return moves


def knight_moves(board: dict[str, str], pos: str, color: str) -> set[str]:
    """Returns a the set of legal moves for a Knight of color color, from position pos, on board board"""
    x, y = coords(pos)

    offsets = [
        (1, 2), (2, 1), (2, -1), (1, -2),
        (-1, -2), (-2, -1), (-2, 1), (-1, 2)
    ]

    moves = set()

    for dx, dy in offsets:
        nx, ny = x + dx, y + dy

        if not on_board(nx, ny):
            continue

        target = position(nx, ny)

        if target not in board or board[target][0] != color:
            moves.add(target)

    return moves


def king_moves(board: dict[str, str], pos: str, color: str) -> set[str]:
    """Returns a the set of legal moves for a King of color color, from position pos, on board board"""
    x, y = coords(pos)

    moves = set()

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue

            nx, ny = x + dx, y + dy

            if not on_board(nx, ny):
                continue

            target = position(nx, ny)

            if target not in board or board[target][0] != color:
                moves.add(target)

    return moves


def sliding_moves(board: dict[str, str], pos: str, color: str, directions: list[tuple[int]]) -> set[str]:
    """Returns a the set of legal moves for a sliding piece (Queen, Bishop or Rook) of color color, from position pos, on board board
    
    The directions are the allowed movement vectors for the piece. They serve as identifiers for the piece"""
    x, y = coords(pos)
    moves = set()

    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        while on_board(nx, ny):
            target = position(nx, ny)

            if target not in board:
                moves.add(target)
            else:
                # We can capture an enemy piece, but can't move
                # through either color's piece.
                if board[target][0] != color:
                    moves.add(target)
                break

            nx += dx
            ny += dy

    return moves


def in_check(board: dict[str, str], color: str) -> bool:
    """Return True if `color`'s king is currently in check."""

    king = color + 'K'
    # Search for the king. This could be upgraded if the kings position is always monitored.
    king_pos = next(
        (pos for pos, piece in board.items() if piece == king),
        None
    )
    # Should trigger an invalid board error since there must always be two kings on a board
    if king_pos is None:
        return True

    opponent = 'b' if color == 'w' else 'w'

    # Check whether any opposing piece attacks the king.
    for pos, piece in board.items():
        if piece[0] != opponent:
            continue

        if attacks(board, pos, king_pos):
            return True

    return False


def attacks(board, source, target):
    """Return True if the piece at source attacks target."""

    color = board[source]
    piece = color[1]
    color = color[0]

    sx, sy = coords(source)
    tx, ty = coords(target)
    dx = tx - sx
    dy = ty - sy

    if piece == 'P':
        direction = 1 if color == 'w' else -1
        return dy == direction and abs(dx) == 1

    if piece == 'N':
        return (abs(dx), abs(dy)) in {(1, 2), (2, 1)}

    if piece == 'K':
        return max(abs(dx), abs(dy)) == 1

    if piece == 'B':
        if abs(dx) != abs(dy):
            return False
        return clear_path(board, sx, sy, tx, ty)

    if piece == 'R':
        if dx != 0 and dy != 0:
            return False
        return clear_path(board, sx, sy, tx, ty)

    if piece == 'Q':
        if dx != 0 and dy != 0 and abs(dx) != abs(dy):
            return False
        return clear_path(board, sx, sy, tx, ty)

    return False


def clear_path(board, sx, sy, tx, ty):
    """Check whether the squares between two positions are empty."""

    step_x = (tx > sx) - (tx < sx)
    step_y = (ty > sy) - (ty < sy)

    x, y = sx + step_x, sy + step_y

    while (x, y) != (tx, ty):
        if position(x, y) in board:
            return False
        x += step_x
        y += step_y

    return True


