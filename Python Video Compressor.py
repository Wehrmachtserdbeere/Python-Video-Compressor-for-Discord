import subprocess

available_sizes = [
    "./program/10mb.py",
    "./program/25mb.py",
    "./program/50mb.py",
    "./program/100mb.py"
]

sizechooser = input("Choose the targeted maximum size:\n(1) 10 mb - Default, will be chosen if input is empty or otherwise unrecognized.\n(2) 25 mb\n(3) 50 mb\n(4) 100 mb\n\nInput: ")

try:
    sizechooser = int(sizechooser)  # Try converting to an integer
    if sizechooser < 1 or sizechooser > len(available_sizes):
        raise ValueError()  # Raise an error if the choice is out of range
except (ValueError, TypeError):  # Catch invalid inputs and default to 1
    sizechooser = 1  # Default to the first option (10mb)

subprocess.call(["python", available_sizes[sizechooser - 1]]) # -1 due to Python listing