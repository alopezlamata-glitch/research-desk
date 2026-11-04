import re, sys
f, a = sys.argv[1], int(sys.argv[2])
b = int(sys.argv[3]) if len(sys.argv) > 3 else a
w = int(sys.argv[4]) if len(sys.argv) > 4 else 2500
t = open(f"../../kb/library/md/{f}.md", encoding="utf8").read()
parts = re.split(r"<!-- p\. (\d+) -->", t)
for i in range(1, len(parts), 2):
    n = int(parts[i])
    if a <= n <= b:
        print(f"\n##### p. {n}\n{parts[i+1].strip()[:w]}")
