import socket
import sys
import threading

PORT = 12345

# Server -> client message types
SRV_BOARD, SRV_SCORE, SRV_DELTA = 0b00, 0b01, 0b10
TILE_CHARS = {0b00: "_", 0b01: "X", 0b10: "1", 0b11: "2"}

# Move directions (top 3 bits); the low 5 bits carry the player: 00000 / 00010
DIRECTIONS = {"up": 0b100, "down": 0b101, "left": 0b110, "right": 0b111}


def command_byte(name, player):
    if name == "print":
        return 0b00100000
    return (DIRECTIONS[name] << 5) | ((player - 1) << 1)


class GameState:
    def __init__(self):
        self.board = []
        self.scores = [0, 0]

    def __str__(self):
        out = f"Scores -> Player 1: {self.scores[0]} | Player 2: {self.scores[1]}\n"
        for row in self.board:
            out += " ".join(row) + "\n"
        return out


def parse_messages(buf, state):
    """Apply every COMPLETE message in buf; return the leftover bytes."""
    events = []
    i = 0
    while i < len(buf):
        kind = buf[i] >> 6
        if kind == SRV_BOARD:
            size = (buf[i] >> 2) & 0xF
            if len(buf) - i < 1 + size * size:
                break
            body = buf[i + 1:i + 1 + size * size]
            state.board = [[chr(b) for b in body[r * size:(r + 1) * size]]
                           for r in range(size)]
            events.append("board received")
            i += 1 + size * size
        elif kind == SRV_SCORE:
            if len(buf) - i < 2:
                break
            state.scores[0] = (buf[i] >> 2) & 0xF
            state.scores[1] = ((buf[i] & 0b11) << 2) | (buf[i + 1] >> 6)
            events.append("scores updated")
            i += 2
        elif kind == SRV_DELTA:
            if len(buf) - i < 2:
                break
            row = (buf[i] >> 2) & 0xF
            col = ((buf[i] & 0b11) << 2) | (buf[i + 1] >> 6)
            value = (buf[i + 1] >> 4) & 0b11
            if row < len(state.board) and col < len(state.board):
                state.board[row][col] = TILE_CHARS[value]
                events.append(f"tile ({row},{col}) -> '{TILE_CHARS[value]}'")
            i += 2
        else:
            i += 1
    return buf[i:], events


def server_listener(s, state, closed):
    buf = b""
    while True:
        try:
            chunk = s.recv(1024)
        except OSError:
            chunk = b""
        if not chunk:
            print("\nServer disconnected (the game may already have 2 players). "
                  "Press Enter to exit.")
            closed.set()
            return
        buf, events = parse_messages(buf + chunk, state)
        if events:
            print("\n--- Board Update: " + "; ".join(events) + " ---")
            print(state)


def main():
    if len(sys.argv) < 3 or sys.argv[2] not in ("1", "2"):
        print("Usage: python3 client.py SERVER_IP 1|2")
        return
    host, player = sys.argv[1], int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, PORT))
    except OSError as e:
        print("Could not connect to the server:", e)
        return

    state = GameState()
    closed = threading.Event()
    threading.Thread(target=server_listener, args=(s, state, closed),
                     daemon=True).start()
    s.sendall(bytes([command_byte("print", player)]))

    while not closed.is_set():
        choice = input(f"Player {player} command (print/up/down/left/right/"
                       "create N/quit): ").strip().lower()
        if closed.is_set() or choice in ("quit", "exit", "q"):
            break
        try:
            if choice == "print" or choice in DIRECTIONS:
                s.sendall(bytes([command_byte(choice, player)]))
            elif choice.startswith("create "):
                s.sendall(bytes([int(choice.split()[1]) << 1]))
            else:
                print("Unknown command.")
        except (ValueError, OSError) as e:
            print("Could not send:", e)
    s.close()


if __name__ == "__main__":
    main()