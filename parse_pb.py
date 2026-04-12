import string

with open(r'C:\Users\chris\.gemini\antigravity\conversations\38e24f50-feeb-49ff-9d72-5be8c09e44a6.pb', 'rb') as f:
    data = f.read()

# Filter printable characters
printable_chars = set(bytes(string.printable, 'ascii'))
filtered = bytearray([b if b in printable_chars else 10 for b in data]).decode('ascii')

# Split by newlines, strip, ignore empty, and join
lines = [line.strip() for line in filtered.split('\n') if len(line.strip()) > 1]
text = '\n'.join(lines)

# Print last 20k characters
print(text[-20000:])
