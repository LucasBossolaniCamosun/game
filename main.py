import asyncio

from Board import Board

PORT = 12345
DEFAULT_SIZE = 10
MAX_PLAYERS = 2

CMD_CREATE = 0b000
CMD_PRINT = 0b001
MOVES = {0b100: 'U', 0b101: 'D', 0b110: 'L', 0b111: 'R'}

SRV_BOARD, SRV_SCORE, SRV_DELTA = 0b00, 0b01, 0b10
VAL_BLANK, VAL_BARRIER, VAL_PLAYER1, VAL_PLAYER2 = 0b00, 0b01, 0b10, 0b11


def create_board(size):
    max_barriers = (size * size // 5) // 4
    max_treasures = size * size // 20
    return Board(size, max_barriers, max_treasures)


def parse_command(byte):
    cmd = byte >> 5
    opt = byte & 0b11111
    if cmd == CMD_CREATE:
        if opt & 1:
            return None
        return ('create', opt >> 1, None)
    if cmd == CMD_PRINT:
        return ('print', None, None)
    if cmd in MOVES:
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
    s1 = (board.players[1].get_score() if 1 in board.players else 0) & 0xF
    s2 = (board.players[2].get_score() if 2 in board.players else 0) & 0xF
    return bytes([(SRV_SCORE << 6) | (s1 << 2) | (s2 >> 2), (s2 & 0b11) << 6])


async def main():
    board = create_board(DEFAULT_SIZE)
    writers = {}                      

    async def send(targets, data):
        for w in targets:
            try:
                w.write(data)
                await w.drain()
            except ConnectionError:
                pass

    async def handle_byte(byte, me):
        nonlocal board
        command = parse_command(byte)
        if command is None:
            return
        kind, arg, player_id = command

        if kind == 'create':
            try:
                new_board = create_board(arg)
            except ValueError:                    
                return
            for pid in board.players:             
                new_board.add_player(pid)
            board = new_board
            print(board)
            await send(list(writers.values()), encode_board(board))

        elif kind == 'print':
            await send([writers[me]], encode_board(board))

        elif kind == 'move' and player_id in board.players:
            old_row, old_col = board.players[player_id].get_position()
            board.move(player_id, arg)
            new_row, new_col = board.players[player_id].get_position()
            print(board)
            reply = (encode_delta(board, old_row, old_col)
                     + encode_delta(board, new_row, new_col)
                     + encode_scores(board))
            await send(list(writers.values()), reply)

    async def handle_client(reader, writer):
        free = [p for p in range(1, MAX_PLAYERS + 1) if p not in writers]
        if not free:                             
            print("Rejected extra connection")
            writer.close()
            return
        me = free[0]
        writers[me] = writer
        board.add_player(me)
        print(f"Player {me} connected")
        print(board)
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                for byte in data:                 
                    await handle_byte(byte, me)
        except ConnectionError:
            pass
        finally:
            del writers[me]
            board.players.pop(me, None)
            writer.close()
            print(f"Player {me} disconnected")

    server = await asyncio.start_server(handle_client, "", PORT)
    print(f"Listening on port {PORT}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())