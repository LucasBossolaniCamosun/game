import constants
import pytest
from Board import Board
from Player import Player


# Required tests 
def test_player():
    p = Player(1, 2, 3, 10)
    assert p.get_position() == (1, 2)
    assert p.get_score() == 3

    p.add_score(10)
    assert p.get_score() == 13
    p.move(constants.UP, constants.BLANK)
    assert p.get_position() == (0, 2)


def test_board():
    with pytest.raises(ValueError, match='Size must be at least 5.'):
        b = Board(0, 0, 0)


# Helper: board with no barriers/treasures and a known player spot
def clean_board(size=5, player_pos=(2, 2)):
    b = Board(size, 0, 0)
    for r in range(size):
        for c in range(size):
            b.board[r][c].contents = '_'
    b.player.row, b.player.col = player_pos
    return b


# Player
def test_player_name_auto_increments():
    p1 = Player(0, 0, 0, 5)
    p2 = Player(0, 0, 0, 5)
    assert int(p2.name) == int(p1.name) + 1


@pytest.mark.parametrize("row, col, score", [(-1, 0, 0), (0, -1, 0), (0, 0, -1)])
def test_player_negative_values_raise(row, col, score):
    with pytest.raises(ValueError):
        Player(row, col, score, 5)


def test_player_outside_board_raises():
    with pytest.raises(ValueError):
        Player(5, 0, 0, 5)


def test_player_add_negative_score_raises():
    p = Player(0, 0, 3, 5)
    with pytest.raises(ValueError):
        p.add_score(-1)


@pytest.mark.parametrize("direction, expected", [
    ('U', (1, 2)), ('D', (3, 2)), ('L', (2, 1)), ('R', (2, 3)),
])
def test_player_move_directions(direction, expected):
    p = Player(2, 2, 0, 5)
    p.move(direction)
    assert p.get_position() == expected


def test_player_move_off_edge_is_ignored():
    p = Player(0, 0, 0, 5)
    p.move('U')
    p.move('L')
    assert p.get_position() == (0, 0)


def test_player_move_invalid_direction_raises():
    p = Player(2, 2, 0, 5)
    with pytest.raises(ValueError):
        p.move('X')


# Board setup and exceptions
def test_board_too_many_barriers_raises():
    with pytest.raises(ValueError, match='20%'):
        Board(5, 2, 0)


def test_board_too_many_treasures_raises():
    with pytest.raises(ValueError, match='5%'):
        Board(5, 0, 2)


def test_board_places_treasures():
    b = Board(10, 0, 5)
    count = sum(t.contents == '$' for row in b.board for t in row)
    assert count == 5


def test_board_player_starts_on_free_tile():
    for _ in range(25):
        b = Board(5, 1, 1)
        assert b.board[b.player.row][b.player.col].contents == '_'


# Board movement
def test_board_move_off_edge_is_ignored():
    b = clean_board(player_pos=(0, 0))
    b.move('U')
    assert b.player.get_position() == (0, 0)


def test_board_move_into_barrier_is_blocked():
    b = clean_board()
    b.board[2][3].contents = 'X'
    b.move('R')
    assert b.player.get_position() == (2, 2)


def test_board_move_onto_treasure_collects_it():
    b = clean_board()
    b.board[2][3].contents = '$'
    b.move('R')
    assert b.player.get_position() == (2, 3)
    assert b.player.get_score() == 1
    assert b.board[2][3].contents == '_'


def test_board_move_invalid_direction_raises():
    b = clean_board()
    with pytest.raises(ValueError):
        b.move('X')


# Normal game play
def test_normal_game_play():
    b = clean_board(size=5, player_pos=(0, 0))
    b.board[0][1].contents = '$'
    b.board[0][2].contents = '$'
    b.board[1][2].contents = 'X'

    b.move('R')                                  
    b.move('R')                                  
    assert b.player.get_position() == (0, 2)
    assert b.player.get_score() == 2

    b.move('D')                                  
    b.move('U')                                  
    assert b.player.get_position() == (0, 2)

    assert "Player Score: 2" in str(b)
def test_board_move_left():
    b = clean_board()
    b.move('L')
    assert b.player.get_position() == (2, 1)
def test_player_str():
    p = Player(1, 2, 3, 5)
    assert str(p) == f"Player {p.name} is at (1, 2) with score: 3"
