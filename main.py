import queue
import socket
import threading
import traceback

from Board import Board

PORT = 12345
DEFAULT_SIZE = 10
MAX_PLAYERS = 2

CMD_CREATE = 0b000
CMD_PRINT = 0b001
MOVES = {0b100: 'U', 0b101: 'D', 0b110: 'L', 0b111: 'R'}

# Server -> client message types (protocol page)
SRV_BOARD, SRV_SCORE, SRV_DELTA = 0b00, 0b01, 0b10

VAL_BLANK, VAL_BARRIER, VAL_PLAYER1, VAL_PLAYER2 = 0b00, 0b01, 0b10, 0b11

JOIN = None     # marker put on input_queue when a new client connects

# The only two shared objects allowed by the lab
input_queue = queue.Queue()
output_queue = queue.Queue()


# ---------------------------------------------------------------- encoding
def create_board(size):
    max_barriers = (size * size // 5) // 4
    max_treasures = size * size // 20
    return Board(size, max_barriers, max_treasures)


def parse_command(byte):
    """Returns (kind, argument, player_id) or None if the byte is invalid."""
    cmd = byte >> 5
    opt = byte & 0b11111
    if cmd == CMD_CREATE:
        if opt & 1:
            return None
        return ('create', opt >> 1, None)
    if cmd == CMD_PRINT:
        return ('print', None, None)
    if cmd in MOVES:
        # OPT = 0000 0 -> player 1, 0001 0 -> player 2
        if opt not in (0b00000, 0b00010):
            return None
        return ('move', MOVES[cmd], (opt >> 1) + 1)
    return None


def encode_board(board):
    header = bytes([(SRV_BOARD << 6) | (board.size << 2)])
    body = bytearray()
    for r in range(board.size):
        for c in range(board.size):
            char = board.board[r][c].contents
            for p in board.players.values():
                if (r, c) == (p.row, p.col):
                    char = p.name
            body.append(ord(char))
    return header + bytes(body)


def tile_value(board, row, col):
    for pid, p in board.players.items():
        if (row, col) == (p.row, p.col):
            return VAL_PLAYER1 if pid == 1 else VAL_PLAYER2
    if board.board[row][col].contents == 'X':
        return VAL_BARRIER
    return VAL_BLANK


def encode_delta(board, row, col):
    value = tile_value(board, row, col)
    first = (SRV_DELTA << 6) | (row << 2) | (col >> 2)
    second = ((col & 0b11) << 6) | (value << 4)
    return bytes([first, second])


def encode_scores(board):
    """Score message = 2 bytes: 01 | score1 (4 bits) | score2 (4 bits) | 000000"""
    s1 = (board.players[1].get_score() if 1 in board.players else 0) & 0xF
    s2 = (board.players[2].get_score() if 2 in board.players else 0) & 0xF
    first = (SRV_SCORE << 6) | (s1 << 2) | (s2 >> 2)
    second = (s2 & 0b11) << 6
    return bytes([first, second])


# ---------------------------------------------------------------- threads
def board_thread_worker():
    """The ONLY thread that creates, reads or changes the board."""
    board = create_board(DEFAULT_SIZE)
    print(board)
    while True:
        try:
            client_id, data = input_queue.get()

            if data is JOIN:                       # a client connected
                board.add_player(client_id)
                print(board)
                continue

            for byte in data:                      # each command is 1 byte
                command = parse_command(byte)
                if command is None:
                    continue
                kind, arg, player_id = command

                if kind == 'create':
                    try:
                        new_board = create_board(arg)
                    except ValueError:             # e.g. size below 5
                        continue
                    for pid in board.players:      # keep the same players
                        new_board.add_player(pid)
                    board = new_board
                    output_queue.put(("ALL", [encode_board(board)]))
                    print(board)

                elif kind == 'print':
                    output_queue.put((client_id, [encode_board(board)]))

                elif kind == 'move':
                    if player_id not in board.players:
                        continue
                    old_row, old_col = board.players[player_id].get_position()
                    board.move(player_id, arg)
                    new_row, new_col = board.players[player_id].get_position()
                    output_queue.put(("ALL", [
                        encode_delta(board, old_row, old_col),
                        encode_delta(board, new_row, new_col),
                        encode_scores(board),
                    ]))
                    print(board)
        except Exception as e:
            print(f"\n--- ERROR IN BOARD THREAD ---\n{e}")
            traceback.print_exc()


def client_read_thread(conn, client_id):
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            input_queue.put((client_id, data))
    except Exception:
        pass
    finally:
        conn.close()
        print(f"Player {client_id} disconnected")


def output_thread_worker(connections):
    while True:
        target, replies = output_queue.get()
        if target == "ALL":
            targets = list(connections.values())   # copy: dict may change
        else:
            targets = [connections.get(target)]
        message = b''.join(replies)
        for conn in targets:
            if conn:
                try:
                    conn.sendall(message)
                except Exception:
                    pass


def main():
    connections = {}
    threading.Thread(target=board_thread_worker, daemon=True).start()
    threading.Thread(target=output_thread_worker, args=(connections,),
                     daemon=True).start()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", PORT))
    server.listen()
    print(f"Listening on port {PORT}")

    player_count = 1
    while True:
        conn, addr = server.accept()
        if player_count <= MAX_PLAYERS:
            print(f"Player {player_count} connected from {addr}")
            connections[player_count] = conn
            input_queue.put((player_count, JOIN))   # board thread adds the player
            threading.Thread(target=client_read_thread,
                             args=(conn, player_count), daemon=True).start()
            player_count += 1
        else:
            print(f"Rejected extra connection from {addr}")
            conn.close()


if __name__ == "__main__":
    main()