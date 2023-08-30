# BOGGLE SOLVER
# By Sam Kauffman
# 2023

# This program solves the game Boggle by generating a list of all valid words
# for a given board. It works for standard Boggle (4x4), Big Boggle (5x5), and
# Super Big Boggle (6x6). It knows the minimum word length for each Boggle
# size. The blank cube from Super Big Boggle can be interpreted as a block
# (as in the official rules) or as a wild (as in Scrabble).

# It requires converted_word_list.json, which is generated by the companion
# script convert_dict.py.

# Select the board size, and then enter the cubes row by row as prompted. A
# cube may be:
#   - any single letter
#   - any pair of letters
#   - a block: #
#   - a wild: *


import json


# Minimum word length
MIN_LENGTHS = {
    4: 3,
    5: 4,
    6: 4,
    }

# Coordinates of the 8 possible directions to step
DIRECTIONS = {
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
}


board = []


# Get size
while True:
    size_input = input('Enter size (4, 5, 6):').strip()
    if size_input in ('4', '5', '6'):
        size = int(size_input)
        break
    print('Invalid value')

# Get input to build the board
print('Enter rows with cubes separated by spaces.')
for n in range(size):
    row = []
    while True:
        row_input = input('Row %d:' % (n + 1))
        cubes = row_input.strip().lower().split()
        if len(cubes) == size:
            for cube in cubes:
                if len(cube) in (1, 2) and (
                        cube in ('#', '*') or (
                            cube[0] in 'abcdefghijklmnopqrstuvwxyz' and (
                                len(cube) == 1
                                or cube[1] in 'abcdefghijklmnopqrstuvwxyz'
                                )
                            )
                        ):
                    row.append(cube)
                else:
                    print('Each cube must be 1 or 2 letters, #, or *')
                    break
            # finished row
            board.append(row)
            break
        else:
            print('Error: Enter %d cubes.' % size)


# Output the board prettily
print()
for row in board:
    pretty_cubes = []
    for cube in row:
        if len(cube) == 1:
            pretty_cubes.append(' ' + cube.upper())
        else:
            pretty_cubes.append(cube.upper())
    print(' '.join(pretty_cubes))


# Get the dictionary
full_dict = json.load(open('converted_word_list.json'))
# Cube coordinates are 0-indexed
max_x = max_y = size - 1
# Min length depends on which size of Boggle you are playing.
min_length = MIN_LENGTHS[size]
# words: The set of valid words found
words = set()
# used_cubes: Cubes that have been used in the current state of word-finding,
# stored by their coordinates. Because the algorithm is basically a tree
# traversal, we have to keep backtracking and therefore we can't modify this
# set but haveto make a new copy of it at each step. It doesn't need to be
# frozen, but that prevents us from accidentally modifying it.
used_cubes = frozenset()

def search_cube(x, y, partial_word, partial_dict, used_cubes, wild_is=None):
    cube = board[y][x]
    cube_good = True

    if wild_is is not None:
        # We are considering one possibility of a wild cube.
        if cube != '*':
            raise Exception('Not a wild')
        else:
            cube = wild_is

    # Iterate through the letters in this cube (there may be one or two)
    for letter in cube:
        if letter == '*':  # wild
            if partial_dict.keys() == ['$']:
                # The only valid thing we can do here is end the word, so the
                # wild is no good.
                cube_good = False
            else:
                # Consider each possibility for the wild (letters, not $) that
                # is valid in the current situation.
                for next_letter in partial_dict.keys():
                    if next_letter != '$':
                        # Recurse at the same coordinates
                        search_cube(x, y, partial_word, partial_dict,
                            used_cubes, wild_is=next_letter)

        elif letter in partial_dict:
            # Letter is good. Keep it and step down the dictionary.
            partial_word += letter
            partial_dict = partial_dict[letter]
        else:
            # a block, or any letter that doesn't produce any valid words
            cube_good = False

    if cube_good:
        # Mark this cube as used
        used_cubes = frozenset(used_cubes | {(x, y)})

        # We can end the word here, therefore this partial word is valid.
        if '$' in partial_dict and len(partial_word) >= min_length:
            words.add(partial_word)

        # For each possible direction to move, within the confines of the
        # board, recurse, as long as it's not a cube we've visited.
        for direction in DIRECTIONS:
            new_x = x + direction[0]
            new_y = y + direction[1]
            if (new_x >= 0 and new_x <= max_x
                    and new_y >= 0 and new_y <= max_y
                    and (new_x, new_y) not in used_cubes):
                search_cube(new_x, new_y, partial_word, partial_dict, used_cubes)    


# Solve
for y in range(size):
    for x in range(size):
        search_cube(x, y, '', full_dict, used_cubes)


# Output results
print()
print('%d words' % len(words))
print()
for word in sorted(list(words)):
    print(word)