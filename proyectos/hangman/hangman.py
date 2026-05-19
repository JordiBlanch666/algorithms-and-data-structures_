"""
Hangman
=======
Author  : Jordi Yashua Contreras Blanch
GitHub  : github.com/JordiBlanch666
Contact : paastor.blanch@gmail.com
Course  : Software Engineering · Hybridge · 2nd semester

Classic word-guessing game with ASCII art, three difficulty levels,
and a built-in word bank organized by category.

Concepts demonstrated:
  - Sets for efficient membership testing (already_guessed)
  - String manipulation (masking letters, replacing characters)
  - Nested functions and clear separation of game logic vs display
  - Random selection from categorized word lists
  - Game loop with multiple exit conditions
"""

import random
import os

# ── Word bank ─────────────────────────────────────────────────────────────────
# Organized by category. Easy words are short and common;
# hard words are longer or less frequent.

WORDS = {
    "easy": [
        "cat", "dog", "sun", "run", "map", "cup", "hat", "bus",
        "key", "box", "pen", "car", "sky", "bed", "arm", "leg",
    ],
    "medium": [
        "python", "bridge", "jungle", "rocket", "winter", "travel",
        "castle", "mirror", "planet", "basket", "garden", "finger",
        "signal", "candle", "branch", "school",
    ],
    "hard": [
        "algorithm", "javascript", "keyboard", "framework", "bandwidth",
        "encryption", "debugging", "recursion", "bootstrap", "interface",
        "middleware", "polymorphism", "abstraction", "inheritance",
    ],
}

# ── ASCII art ─────────────────────────────────────────────────────────────────
# Each stage corresponds to the number of wrong guesses (0 = untouched, 6 = dead).

STAGES = [
    # 0 wrong guesses
    """
       -----
       |   |
       |
       |
       |
       |
    --------""",
    # 1
    """
       -----
       |   |
       |   O
       |
       |
       |
    --------""",
    # 2
    """
       -----
       |   |
       |   O
       |   |
       |
       |
    --------""",
    # 3
    """
       -----
       |   |
       |   O
       |  /|
       |
       |
    --------""",
    # 4
    """
       -----
       |   |
       |   O
       |  /|\\
       |
       |
    --------""",
    # 5
    """
       -----
       |   |
       |   O
       |  /|\\
       |  /
       |
    --------""",
    # 6 — game over
    """
       -----
       |   |
       |   O
       |  /|\\
       |  / \\
       |
    --------""",
]

MAX_WRONG = len(STAGES) - 1   # 6 wrong guesses allowed


# ── Display helpers ───────────────────────────────────────────────────────────

def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def masked_word(word: str, guessed: set[str]) -> str:
    """
    Replace unguessed letters with underscores.
    'python' with {'p','y'} guessed → 'p y _ _ _ _'
    """
    return " ".join(letter if letter in guessed else "_" for letter in word)


def print_board(word: str, guessed: set[str], wrong: set[str], difficulty: str) -> None:
    clear()
    wrong_count = len(wrong)
    print(STAGES[wrong_count])
    print(f"\n  Difficulty: {difficulty.upper()}  |  Wrong guesses left: {MAX_WRONG - wrong_count}")
    print(f"\n  {masked_word(word, guessed)}\n")
    if wrong:
        print(f"  Wrong letters: {' '.join(sorted(wrong))}\n")


# ── Game logic ────────────────────────────────────────────────────────────────

def choose_word(difficulty: str) -> tuple[str, str]:
    """Pick a random word from the chosen difficulty level."""
    word = random.choice(WORDS[difficulty])
    category = difficulty   # in this version, category == difficulty
    return word, category


def is_won(word: str, guessed: set[str]) -> bool:
    """The player wins when every letter in the word has been guessed."""
    return all(letter in guessed for letter in word)


def play_round(difficulty: str) -> bool:
    """
    Run one full round. Returns True if the player won, False if they lost.
    """
    word, _ = choose_word(difficulty)
    guessed: set[str] = set()   # all correct guesses
    wrong: set[str] = set()     # incorrect guesses only

    while True:
        print_board(word, guessed, wrong, difficulty)

        # Win check — placed before asking for input so the final state is shown.
        if is_won(word, guessed):
            print(f"  You won! The word was '{word}'. 🎉\n")
            return True

        if len(wrong) >= MAX_WRONG:
            print(f"  Game over! The word was '{word}'.\n")
            return False

        raw = input("  Guess a letter: ").strip().lower()

        if len(raw) != 1 or not raw.isalpha():
            print("  Please enter a single letter.\n")
            input("  Press Enter to continue...")
            continue

        if raw in guessed or raw in wrong:
            print(f"  You already guessed '{raw}'.")
            input("  Press Enter to continue...")
            continue

        # Update the appropriate set based on whether the guess is correct.
        if raw in word:
            guessed.add(raw)
        else:
            wrong.add(raw)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    clear()
    print("\n╔══════════════════════════════════════╗")
    print("║              Hangman                 ║")
    print("║   Jordi Yashua Contreras Blanch      ║")
    print("╚══════════════════════════════════════╝\n")

    wins = 0
    losses = 0

    while True:
        print(f"  Record: {wins}W / {losses}L\n")
        print("  Difficulty:  [1] Easy   [2] Medium   [3] Hard")
        print("               [q] Quit\n")
        choice = input("  Choose: ").strip().lower()

        difficulty_map = {"1": "easy", "2": "medium", "3": "hard"}

        if choice == "q":
            print(f"\n  Thanks for playing! Final record: {wins}W / {losses}L\n")
            break
        elif choice not in difficulty_map:
            print("  Invalid option.\n")
            continue

        difficulty = difficulty_map[choice]
        won = play_round(difficulty)

        if won:
            wins += 1
        else:
            losses += 1

        input("  Press Enter to return to menu...")
        clear()


if __name__ == "__main__":
    main()
