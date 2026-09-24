#!/usr/bin/env python3

import sys

current_word = None
current_total = 0

for line in sys.stdin:
    word, value = line.rstrip("\n").split("\t", 1)
    value = int(value)

    if word == current_word:
        current_total += value
    else:
        if current_word is not None:
            print(f"{current_word}\t{current_total}")
        
        current_word = word
        current_total = value

if current_word is not None:
    print(f"{current_word}\t{current_total}")