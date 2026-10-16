from Player import Player
from random import randint
from Tile import Tile

class Board:
    def __init__(self, size, numBarriers, numTreasures):
        """
        Initializes the board, validates the parameters, and sets up 
        the grid before placing barriers and treasures.
        """
        if size < 5:
            raise ValueError("Size must be at least 5.")
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
        
        # Place the player on a free tile
        while True:
            r = randint(0, self.size - 1)
            c = randint(0, self.size - 1)
            if self.board[r][c].contents == '_':
                self.player = Player(r, c, 0, self.size)
                break

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
                
    def move(self, direction):
        """
        Attempts to move the player in the given direction.
        Handles boundary checks, barrier collisions, and treasure collection.
        """
        # Validate direction to throw ValueError to be caught in main.py
        if direction not in ['U', 'D', 'L', 'R']:
            raise ValueError("Invalid direction.")
            
        # Calculate the intended new position
        new_row = self.player.row
        new_col = self.player.col
        
        if direction == 'U':
            new_row -= 1
        elif direction == 'D':
            new_row += 1
        elif direction == 'L':
            new_col -= 1
        elif direction == 'R':
            new_col += 1
            
        # Don't move if stepping beyond the board boundary
        if new_row < 0 or new_row >= self.size or new_col < 0 or new_col >= self.size:
            return  
            
        # Don't move if running into a barrier
        if self.board[new_row][new_col].contents == 'X':
            return  
            
        # If the move is valid, call the player's move method
        self.player.move(direction)
        
        # If the tile contains a treasure, replace with a blank and add score
        if self.board[new_row][new_col].contents == '$':
            self.board[new_row][new_col].contents = '_'  
            self.player.add_score(1)

    def __str__(self):
        """
        Overrides default printing to return a formatted string. 
        Includes the player's score and shows the player's location on the board.
        """
        output = f"Player Score: {self.player.get_score()}\n"
        for r in range(self.size):
            row_list = []
            for c in range(self.size):
                # Print the player's name if they are on this tile
                if r == self.player.row and c == self.player.col:
                    row_list.append(self.player.name)
                else:
                    row_list.append(self.board[r][c].contents)
            output += " ".join(row_list) + "\n"
        return output