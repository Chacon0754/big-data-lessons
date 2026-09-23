from __future__ import annotations
import re
import sys
import time
import math
import os
from collections import defaultdict
from concurrent.futures import Executor, ThreadPoolExecutor, ProcessPoolExecutor
from typing import Final, Literal

Pair  = tuple[str, int]
Pairs = list[Pair]
Grouped = dict[str, list[int]]
Partition = list[tuple[str, list[int]]]
Counts = dict[str, int]
Mode = Literal["sequential", "threads", "processes"]


WORD_RE: Final[re.Pattern[str]] = re.compile(r"[a-záéíóúüñ]+", re.IGNORECASE)

STOPWORDS: Final[frozenset[str]] = frozenset({"de", "la", "el", "y", "a", "en", "que", "los", "las", "un",
             "una", "por", "con", "del", "se", "al", "es", "lo", "su"})

def split_text(text: str, n_chunks: int)-> list[str]:
    lines: list[str] = text.splitlines(keepends=True)
    size: int = math.ceil(len(lines) / n_chunks)
    return ["".join(lines[i:i + size]) for i in range(0, len(lines), size)]

def map_chunk(chunk: str) -> Pairs:
    pairs: Pairs = []

    for word in WORD_RE.findall(chunk.lower()):
        if word not in STOPWORDS:
            pairs.append((word, 1))
    return pairs

def shuffle(mapped: list[Pairs]) -> Grouped:
    grouped: defaultdict[str, list[int]] = defaultdict(list)
    for pairs in mapped:
        for word, one in pairs:
            grouped[word].append(one)
    return dict(grouped)

def partition(grouped: Grouped, n_parts: int) -> list[Partition]:
    items: Partition = list(grouped.items())
    size: int = math.ceil(len(items) / n_parts) or 1
    return [items[i:i + size] for i in range(0, len(items), size)]

def reduce_partition(part: Partition) -> Counts:
    return {word: sum(values) for word, values in part}

def merge(partials: list[Counts]) -> Counts:
    final: Counts = {}
    for partial in partials:
        for word, total in partial.items():
            final[word] = final.get(word, 0) + total
    return final

def word_count(text: str, n_workers: int = 4, mode: Mode = "processes") -> Counts:
    chunks: list[str] = split_text(text, n_workers)

    if mode == "sequential":
        mapped: list[Pairs] = [map_chunk(c) for c in chunks]
        grouped: Grouped = shuffle(mapped)
        partials: list[Counts] = [reduce_partition(p) for p in partition(grouped, n_workers)]
    
    else: 
        pool: Executor = (
            ThreadPoolExecutor(max_workers=n_workers) if mode == "threads"
            else ProcessPoolExecutor(max_workers=n_workers)
    )
        with pool:
            mapped = list(pool.map(map_chunk, chunks))
            grouped = shuffle(mapped)
            partials = list(pool.map(reduce_partition, partition(grouped, n_workers)))

    return merge(partials)

SAMPLE_TEXT: Final[str] = """El veloz murcielago hindu comia feliz cardillo y kiwi
la ciguena tocaba el saxofon detras del palenque de paja
el perro come carne y el gato come pescado
Python es un lenguaje de programacion interpretado
MapReduce divide el trabajo entre varios trabajadores
cada trabajador procesa una parte del texto
el resultado final se combina en un solo diccionario
la programacion paralela mejora el rendimiento
"""


def main() -> None:
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as handle:
            text: str = handle.read()
    else:
        text = SAMPLE_TEXT
 
    n_workers: int = os.cpu_count() or 4
    print(f"Available cores: {n_workers}")
    print(f"Text size: {len(text):,} characters\n")
 
    counts: Counts = {}
    modes: tuple[Mode, ...] = ("sequential", "threads", "processes")
    for mode in modes:
        start: float = time.perf_counter()
        counts = word_count(text, n_workers=n_workers, mode=mode)
        elapsed: float = time.perf_counter() - start
        print(f"{mode:<12} {elapsed:6.2f} s   ({len(counts):,} unique words)")
 
    print("\nTop 10 most frequent words:")
    for word, total in sorted(counts.items(), key=lambda kv: -kv[1])[:10]:
        print(f"  {word:<15} {total:,}")
 
 
if __name__ == "__main__": 
    main()