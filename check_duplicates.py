import re
from collections import Counter

with open('Brnmain.py', encoding='utf-8') as f:
    content = f.read()

methods = re.findall(r'def (\w+)\s*\(', content)
dups = {k: v for k, v in Counter(methods).items() if v > 1}

print('Duplicate methods in Brnmain.py:')
for m, c in sorted(dups.items()):
    print(f'  {m}: {c} times')

# Find line numbers
lines = content.split('\n')
for m in sorted(dups.keys()):
    positions = [i+1 for i, l in enumerate(lines) if re.match(rf'\s+def {m}\s*\(', l)]
    print(f'\n  {m} defined at lines: {positions}')

# Also check for on_place_saved duplicate
print()
print('on_place_saved definitions:')
positions = [i+1 for i, l in enumerate(lines) if re.match(r'\s+def on_place_saved\s*\(', l)]
print(f'  Lines: {positions}')