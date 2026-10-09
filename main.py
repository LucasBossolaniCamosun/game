from Board import Board

b = Board(10, 5, 5)

# Repeatedly print the board and prompt the user
while True:
    print(b)
    direction = input("Enter a direction (U, D, L, R): ")
    
    try:
        # Uses board.move() to prevent accessing instance variables directly[cite: 5]
        b.move(direction)
    except ValueError:
        # On error, print out an error message, but continue prompting[cite: 5]
        print("Error: Invalid direction. Please use U, D, L, or R.")