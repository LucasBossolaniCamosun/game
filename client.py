import socket
import sys

PORT = 12345

COMMANDS = {
    "print": 0b00100000,
    "up":    0b10000000,
    "down":  0b10100000,
    "left":  0b11000000,
    "right": 0b11100000,
}

SRV_BOARD, SRV_SCORE, SRV_DELTA = 0b00, 0b01, 0b10
VAL_BLANK, VAL_BARRIER, VAL_PLAYER = 0b00, 0b01, 0b10


class GameState:
    """Local copy of the board, kept up to date from server messages."""

    def __init__(self):
        self.board = []        
        self.score = None      
        self.player = "1"      

    def __str__(self):
        score = "?" if self.score is None else self.score
        out = f"Player Score: {score}\n"
        for row in self.board:
            out += " ".join(row) + "\n"
        return out


def send_command(host, byte):
    """Connect, send one command byte, read until the server closes, return bytes."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, PORT))
        s.sendall(bytes([byte]))
        data = b""
        while True:
            chunk = s.recv(1024)
            if not chunk:
                break
            data += chunk
    return data


def apply_messages(data, state):
    """Parse every message in `data` and update `state`."""
    i = 0
    while i < len(data):
        kind = data[i] >> 6
        if kind == SRV_BOARD:
            size = (data[i] >> 2) & 0xF
            body = data[i + 1 : i + 1 + size * size]
            if len(body) < size * size:
                print("Warning: board message was cut short")
                break
            state.board = [
                [chr(b) for b in body[r * size : (r + 1) * size]]
                for r in range(size)
            ]
            for row in state.board:         
                for ch in row:
                    if ch.isdigit():
                        state.player = ch
            i += 1 + size * size
        elif kind == SRV_SCORE:
            state.score = (data[i] >> 2) & 0xF
            i += 1
        elif kind == SRV_DELTA:
            if i + 1 >= len(data):
                print("Warning: delta message was cut short")
                break
            row = (data[i] >> 2) & 0xF
            col = ((data[i] & 0b11) << 2) | (data[i + 1] >> 6)
            value = (data[i + 1] >> 4) & 0b11
            if row < len(state.board) and col < len(state.board):
                state.board[row][col] = {
                    VAL_BLANK: "_",
                    VAL_BARRIER: "X",
                    VAL_PLAYER: state.player,
                }.get(value, "_")
            i += 2
        else:
            print("Warning: unknown message type, ignoring the rest")
            break


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else input("Server IP: ").strip()
    state = GameState()

    try:
        data = send_command(host, COMMANDS["print"])
    except OSError as e:
        print("Could not connect to the server:", e)
        return
    apply_messages(data, state)
    print(state)

    while True:
        choice = input("Command (print/up/down/left/right, or quit): ").strip().lower()
        if choice in ("quit", "exit", "q"):
            break
        if choice not in COMMANDS:
            print("Unknown command.")
            continue
        try:
            data = send_command(host, COMMANDS[choice])
        except OSError as e:
            print("Connection problem:", e)
            continue
        apply_messages(data, state)
        print(state)


if __name__ == "__main__":
    main()