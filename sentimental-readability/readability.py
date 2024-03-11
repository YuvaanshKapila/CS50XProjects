from cs50 import get_string
import string

# Get user input
sentence = get_string("Text: ")

# Declare variables
letters = 0
words = 1
sentences = 0

# Loop through string, identifying each letter
for letter in sentence:
    if letter == "!" or letter == "?" or letter == ".":
        sentences += 1
    elif letter in string.punctuation:
        continue
    elif letter in string.whitespace:
        words += 1
    else:
        letters += 1

# Calculations for liau index
wordFactor = words / 100
lettersPer100 = letters / wordFactor
sentencesPer100 = sentences / wordFactor
liauIndex = round((0.0588 * lettersPer100) - (0.296 * sentencesPer100) - 15.8)

# Print correct grade based on liau indx
if liauIndex > 16:
    print("Grade 16+")
elif liauIndex < 1:
    print("Before Grade 1")
else:
    print(f"Grade {liauIndex}")
