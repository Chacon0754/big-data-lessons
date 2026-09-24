from pathlib import Path

directory = Path(__file__).resolve().parent / "data"

block = (
    "Hadoop procesa datos. \n"
    "Docker ejecuta Hadoop. \n"
    "MapReduce cuenta palabras. \n"
)

number_files = 12
repetitions = 50_000
content = block * repetitions
total_bytes = 0

for number in range(1, number_files + 1):
    file = directory / f"input-{number:02d}.txt"
    file.write_text(content, encoding="utf-8")
    total_bytes += file.stat().st_size

print(f"Generated files: {number_files}")
print(f"Total bytes: {total_bytes}")
print(f"Total size: {total_bytes / (1024 ** 2):.2f} MiB")
print(f"Total lines: {number_files * repetitions * 3}")