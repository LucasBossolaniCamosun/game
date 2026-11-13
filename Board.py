from Player import Player
from random import randint
from Tile import Tile

class Board:
    def __init__(self, size, numBarriers, numTreasures):
        if size < 5:
            raise ValueError("Size must be at least 5.")
        self.size = size
        self.numBarriers = numBarriers
        self.numTreasures = numTreasures
        
        boardSize = size * size
        
        if (numBarriers * 4) > (boardSize * 0.2):
            raise ValueError("The barriers cannot take up more than 20% of the board.")
            
        if numTreasures > (boardSize * 0.05):
            raise ValueError("The treasures cannot take up more than 5% of the board.")
            
        self.board = [[Tile('_') for _ in range(self.size)] for _ in range(self.size)]
        self.players = {} # Dictionary mapping player_id to Player object
        
        self.place_barriers()
        self.place_treasures()

    def add_player(self, player_id):
        """Spawns a new player on a free tile."""
        while True:
            r = randint(0, self.size - 1)
            c = randint(0, self.size - 1)
            occupied = any((p.row, p.col) == (r, c) for p in self.players.values())
            if self.board[r][c].contents == '_' and not occupied:
                self.players[player_id] = Player(r, c, 0, self.size)
                # Force the name to match the player_id for protocol simplicity
                self.players[player_id].name = str(player_id)
                break

    def place_barriers(self):
        barrier_corners = []
        placed = 0
        while placed < self.numBarriers:
            r = randint(0, self.size - 1)
            c = randint(0, self.size - 1)
            if (r, c) not in barrier_corners:
                barrier_corners.append((r, c))
                self.board[r % self.size][c % self.size].contents = 'X'
                self.board[(r + 1) % self.size][c % self.size].contents = 'X'
                self.board[r % self.size][(c + 1) % self.size].contents = 'X'
                self.board[(r + 1) % self.size][(c + 1) % self.size].contents = 'X'
                placed += 1

    def place_treasures(self):
        placed = 0
        while placed < self.numTreasures:
            r = randint(0, self.size - 1)
            c = randint(0, self.size - 1)
            if self.board[r][c].contents == '_':
                self.board[r][c].contents = '$'
                placed += 1
                
    def move(self, player_id, direction):
        if direction not in ['U', 'D', 'L', 'R']:
            raise ValueError("Invalid direction.")
        
        if player_id not in self.players:
            return

        player = self.players[player_id]
        new_row, new_col = player.row, player.col
        
        if direction == 'U': new_row -= 1
        elif direction == 'D': new_row += 1
        elif direction == 'L': new_col -= 1
        elif direction == 'R': new_col += 1
            
        if new_row < 0 or new_row >= self.size or new_col < 0 or new_col >= self.size:
            return  
            
        if self.board[new_row][new_col].contents == 'X':
            return  
            
        # Prevent moving onto the other player
        for pid, p in self.players.items():
            if pid != player_id and p.row == new_row and p.col == new_col:
                return

        player.move(direction)
        
        if self.board[new_row][new_col].contents == '$':
            self.board[new_row][new_col].contents = '_'  
            player.add_score(1)

    def __str__(self):
        output = ""
        for pid, p in self.players.items():
            output += f"Player {pid} Score: {p.get_score()} | "
        output += "\n"

        for r in range(self.size):
            row_list = []
            for c in range(self.size):
                occupied = False
                for pid, p in self.players.items():
                    if r == p.row and c == p.col:
                        row_list.append(p.name)
                        occupied = True
                        break
                if not occupied:
                    row_list.append(self.board[r][c].contents)
            output += " ".join(row_list) + "\n"
        return output