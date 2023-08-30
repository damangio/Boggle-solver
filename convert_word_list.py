# Accepts a word list filename, or if none is given uses word_list.txt. Converts
# the word list into a tree, implemented as a nested dict where keys are single
# letters, and values are dictionaries containing everything that can follow the
# letter. $ means the end of a word.


import json
import sys


def add_chars(chars, partial_dict):
    if chars == '' or chars[0] == '\n':
        # End of a word (newline may or may not be present at end of file)
        # Value doesn't matter, only the presence of the $ key.
        partial_dict['$'] = None
    else:
        # Advance to the next letter, and step down the tree.
        add_chars(chars[1:], partial_dict.setdefault(chars[0].lower(), {}))


if len(sys.argv) > 1:
    word_list_filenamename = sys.argv[1]
else:
    word_list_filename = 'word_list.txt'

old_file = open(word_list_filename)
tree = {}

for line in old_file.readlines():
    add_chars(line, tree)

new_file = open('converted_word_list.json', 'w')
json.dump(tree, new_file)
new_file.close()
