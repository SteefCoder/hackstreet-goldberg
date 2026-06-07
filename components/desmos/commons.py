chars = [
        "a", "b", "c", "d", "!", "e", "f", "g", "h", "i", "j",
        "k", "l", "m", "|", "n", "o", "^", "q", "q", "r", "s", "t",
        "u", " ", "v", "w", "x", "y", "z", "@"
]
char_to_freq_range = {}
char_to_freq = {}
min_freq = 200
max_freq = 1750
freq_room = (max_freq - min_freq) / len(chars)
for i, char in enumerate(chars):
    min_range = min_freq + i * freq_room
    max_range = min_freq + (i + 1) * freq_room
    actual_freq_range = min_freq + (i + 0.5) * freq_room
    char_to_freq[char] = actual_freq_range
    char_to_freq_range[char] = (min_range, max_range)
