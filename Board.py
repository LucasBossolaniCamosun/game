from random import randint
from Tile import Tile

class Board:
    def __init__(self, size, numBarriers, numTreasures):
        """
        Initializes the board, validates the parameters, and sets up 
        the grid before placing barriers and treasures.
        """
        self.size = size
        self.numBarriers = numBarriers
        self.numTreasures = numTreasures
        
        boardSize = size * size
        
        # error handling: A barrier is 4 tiles. Calculate total custom tiles to check 20%/5% limit.
        if (numBarriers * 4) > (boardSize * 0.2):
            raise ValueError("The barriers cannot take up more than 20% of the board.")
            
        if numTreasures > (boardSize * 0.05):
            raise ValueError("The treasures cannot take up more than 5% of the board.")
            
        # Create a size x size board of empty Tiles
        self.board = [[Tile('_') for _ in range(self.size)] for _ in range(self.size)]
        
        # Call helper methods to place items
        self.place_barriers()
        self.place_treasures()

    def place_barriers(self):
        """
        Randomly places 2x2 barriers ('X'). Uses the modulo operator (%) 
        to safely wrap around edges. Ensures the starting corner is unique 
        so barriers don't completely replace one another.
        """
        barrier_corners = []
        placed = 0
        
        while placed < self.numBarriers:
            # Pick a random top-left corner for the 2x2 block
            r = randint(0, self.size - 1)
            c = randint(0, self.size - 1)
            
            # Check if this exact corner has already been used
            if (r, c) not in barrier_corners:
                barrier_corners.append((r, c))
                
                # Place the 4 tiles, using modulo (%) to wrap around board edges
                self.board[r % self.size][c % self.size].contents = 'X'
                self.board[(r + 1) % self.size][c % self.size].contents = 'X'
                self.board[r % self.size][(c + 1) % self.size].contents = 'X'
                self.board[(r + 1) % self.size][(c + 1) % self.size].contents = 'X'
                
                placed += 1

    def place_treasures(self):
        """
        Randomly places treasures ('$') one by one. 
        Only places a treasure if the selected tile is currently empty.
        """
        placed = 0
        
        while placed < self.numTreasures:
            r = randint(0, self.size - 1)
            c = randint(0, self.size - 1)
            
            # Check if the tile is completely empty before placing
            if self.board[r][c].contents == '_':
                self.board[r][c].contents = '$'
                placed += 1

    def __str__(self):
        """
        Overrides default printing to return a formatted string. 
        This is required so `print(b)` works correctly in main.py.
        """
        output = ""
        for row in self.board:
            row_list = []
            for tile in row:
                row_list.append(tile.contents)
            output += " ".join(row_list) + "\n"
        return output



