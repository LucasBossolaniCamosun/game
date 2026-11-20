import asyncio
import sys

PORT = 12345

SRV_BOARD, SRV_SCORE, SRV_DELTA = 0b00, 0b01, 0b10
TILE_CHARS = {0b00: "_", 0b01: "X", 0b10: "1", 0b11: "2"}
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


async def listen(reader, state):
    buf = b""
    while True:
        chunk = await reader.read(1024)
        if not chunk:
            print("\nServer disconnected. Press Enter to exit.")
            return
        buf, events = parse_messages(buf + chunk, state)
        if events:
            print("\n--- Board Update: " + "; ".join(events) + " ---")
            print(state)


async def main():
    if len(sys.argv) < 3 or sys.argv[2] not in ("1", "2"):
        print("Usage: python3 client.py SERVER_IP 1|2")
        return
    host, player = sys.argv[1], int(sys.argv[2])

    try:
        reader, writer = await asyncio.open_connection(host, PORT)
    except OSError as e:
        print("Could not connect to the server:", e)
        return

    state = GameState()
    listener = asyncio.create_task(listen(reader, state))
    writer.write(bytes([command_byte("print", player)]))

    while not listener.done():
        choice = await asyncio.to_thread(
            input, f"Player {player} command (print/up/down/left/right/create N/quit): ")
        choice = choice.strip().lower()
        if listener.done() or choice in ("quit", "exit", "q"):
            break
        if choice == "print" or choice in DIRECTIONS:
            writer.write(bytes([command_byte(choice, player)]))
        elif choice.startswith("create ") and choice.split()[1].isdigit():
            writer.write(bytes([int(choice.split()[1]) << 1]))
        else:
            print("Unknown command.")
        await writer.drain()

    listener.cancel()
    writer.close()


if __name__ == "__main__":
    asyncio.run(main())