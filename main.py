import socket 
from Board import Board

PORT = 12345
DEFAULT_SIZE = 10

CMD_CREATE = 0b000
MOVES = {0b100: 'U', 0b101: 'D', 0b110: 'L', 0b111: 'R'}

SRV_BOARD = 0b00
SRV_SCORE = 0b01
SRV_DELTA = 0b10

VAL_BLANK, VAL_BARRIER, VAL_PLAYER = 0b00, 0b01, 0b10

def create_board(size):
    max_barriers = (size * size // 5) // 4 
    max_treasures = size * size // 20        
    return Board(size, max_barriers, max_treasures)

def parse_command(data):
    if len(data) != 1:
        return None
    byte = data[0]
    cmd = byte >> 5
    opt = byte & 0b11111
    if cmd == CMD_CREATE:
        if opt & 1:                  
            return None
        return ('create', opt >> 1)  
    if cmd in MOVES and opt == 0:
        return ('move', MOVES[cmd])
    return None         
def encode_board(board):
    header = bytes([(SRV_BOARD << 6) | (board.size << 2)])
    body = bytearray()
    for r in range(board.size):
        for c in range(board.size):
            if (r, c) == board.player.get_position():
                body.append(ord(board.player.name[0]))
            else:
                body.append(ord(board.board[r][c].contents))
    return header + bytes(body)


def encode_score(board):
    return bytes([(SRV_SCORE << 6) | ((board.player.get_score() & 0xF) << 2)])


def tile_value(board, row, col):
    if (row, col) == board.player.get_position():
        return VAL_PLAYER
    if board.board[row][col].contents == 'X':
        return VAL_BARRIER
    return VAL_BLANK


def encode_delta(board, row, col):
    value = tile_value(board, row, col)
    first = (SRV_DELTA << 6) | (row << 2) | (col >> 2)
    second = ((col & 0b11) << 6) | (value << 4)
    return bytes([first, second])           

def handle_message(data, board):
    """Return (list of reply messages, board). No replies means 'ignored'."""
    command = parse_command(data)
    if command is None:
        return [], board

    kind, arg = command
    if kind == 'create':
        try:
            board = create_board(arg)
        except ValueError:          # e.g. size below 5
            return [], board
        return [encode_board(board)], board

    # motion command
    old_row, old_col = board.player.get_position()
    board.move(arg)
    new_row, new_col = board.player.get_position()
    return [encode_delta(board, old_row, old_col),
            encode_delta(board, new_row, new_col),
            encode_score(board)], board

def print_hex(data):
    print(" ".join(f"{byte:02x}" for byte in data))


def print_game(board):
    print(board)    # Board.__str__ already includes the score


def serve(board):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", PORT))
    server.listen()
    print(f"Listening on port {PORT}")

    while True:
        conn, addr = server.accept()
        try:
            data = conn.recv(1024)
            print_hex(data)
            replies, board = handle_message(data, board)
            for reply in replies:
                conn.sendall(reply)
            if replies:
                print_game(board)
        except Exception as e:       # one bad client must not crash the server
            print("Error handling client:", e)
        finally:
            conn.close()

def main():
    board = create_board(DEFAULT_SIZE)
    print_game(board)
    serve(board)

if __name__ == "__main__":
    main()