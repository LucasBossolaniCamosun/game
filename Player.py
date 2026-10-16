class Player:
    """
    A player on the game board.

    Class attributes:
        next_player_id (int): The name that will be given to the next Player
            created. Starts at 1 and increases by 1 for every new Player.
    """
    next_player_id = 1

    def __init__(self, row, col, score, board_size):
        """
        Creates a Player and automatically assigns it a name.

        Args:
            row (int): The player's starting row.
            col (int): The player's starting column.
            score (int): The player's starting score.
            board_size (int): The width/height of the (square) board.

        Raises:
            ValueError: If row, col, or score is negative.
            ValueError: If row or col is outside the board boundary.
        """
        if row < 0 or col < 0 or score < 0:
            raise ValueError("Row, column, or score cannot be negative.")

        if row >= board_size or col >= board_size:
            raise ValueError("Row or column is outside of the board boundary.")

        self.name = str(Player.next_player_id)
        Player.next_player_id += 1

        self.row = row
        self.col = col
        self.score = score
        self.board_size = board_size

    def get_position(self):
        """
        Returns:
            tuple: The player's location as (row, col).
        """
        return (self.row, self.col)

    def add_score(self, points):
        """
        Adds points to the player's existing score.

        Args:
            points (int): The amount to add.

        Raises:
            ValueError: If points is negative.
        """
        if points < 0:
            raise ValueError("Cannot add a negative score.")
        self.score += points

    def get_score(self):
        """
        Returns:
            int: The player's current score.
        """
        return self.score

    def move(self, direction, extra=None):
        """
        Moves the player one cell in the given direction, if possible.
        If the move would leave the board, the command is ignored.

        Args:
            direction (str): 'U', 'D', 'L', or 'R'.
            extra: Accepted (and ignored) so the provided test, which passes
                a second argument, still runs.

        Raises:
            ValueError: If direction is not one of 'U', 'D', 'L', 'R'.
        """
        if direction not in ('U', 'D', 'L', 'R'):
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
        Returns:
            str: A description of the player's name, position, and score.
        """
        return ("Player " + self.name + " is at (" + str(self.row) + ", "
                + str(self.col) + ") with score: " + str(self.score))