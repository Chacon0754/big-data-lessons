#!/usr/bin/env python3

import re
import sys

WORD_RE = re.compile(r"[0-9a-záéíóúüñ]+", re.IGNORECASE)

for line in sys.stdin:
    words = WORD_RE.findall(line.lower())

    for word in words:
        print(f"{word}\t1")