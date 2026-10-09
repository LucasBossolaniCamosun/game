class Player:
    """
    Class variable to keep track of the next available player name.
    Starts at 1 and increments every time a new Player is created
    """
    next_player_id = 1

    def __init__(self, row, col, board_size, score=0):
        """
        Initializes the player with coordinates, board size, and score.
        Automatically assigns the name and validates all inputs.
        """
        # Throws a ValueError if row, column, or the score are negative
        if row < 0 or col < 0 or score < 0:
            raise ValueError("Row, column, or score cannot be negative.")
            
        # Throws a ValueError if row or column would be placed outside of the board boundary[cite: 4]
        if row >= board_size or col >= board_size:
            raise ValueError("Row or column is outside of the board boundary.")

        # Contains a name string that is automatically set and increments by 1
        self.name = str(Player.next_player_id)
        Player.next_player_id += 1

        self.row = row
        self.col = col
        self.board_size = board_size
        self.score = score

    def add_score(self, points):
        """
        Takes a score to be added to the existing score[cite: 4].
        Throws a ValueError if the score is negative[cite: 4].
        """
        if points < 0:
            raise ValueError("Cannot add a negative score.")
        self.score += points

    def get_score(self):
        """
        Returns the current score[cite: 4].
        """
        return self.score

    def move(self, direction):
        """
        Takes a direction (U, D, L, R) to change the Player's location[cite: 4].
        If moving pushes the player out of bounds, the command is ignored[cite: 4].
        Throws a ValueError if the direction is invalid[cite: 4].
        """
        if direction not in ['U', 'D', 'L', 'R']:
            raise ValueError("Invalid direction. Use U, D, L, or R.")

        if direction == 'U' and self.row > 0:
            self.row -= 1
        elif direction == 'D' and self.row < self.board_size - 1:
            self.row += 1
        elif direction == 'L' and self.col > 0:
            self.col -= 1
        elif direction == 'R' and self.col < self.board_size - 1:
            self.col += 1

    def __str__(self):
        """
        Provides a string representation of the player's status[cite: 4].
        """
        return "Player " + self.name + " is at (" + str(self.row) + ", " + str(self.col) + ") with score: " + str(self.score)