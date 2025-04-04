import random
import string
import os
import sys
import json
import time

# --- Constants ---
WORDS_FILENAME = "words.txt"
HIGH_SCORES_FILENAME = "high_scores.json"
MAX_HIGH_SCORES = 10

# Difficulty Settings (Lives)
DIFFICULTY_LEVELS = {
    "easy": 8,
    "medium": 6,
    "hard": 4
}

# Scoring
SCORE_CORRECT_GUESS = 10
SCORE_INCORRECT_GUESS = -5
SCORE_HINT_PENALTY = -15
SCORE_WIN_BONUS = 50

# ANSI Color Codes
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_MAGENTA = "\033[95m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"

# Hangman ASCII Art Stages (Slightly enhanced)
HANGMAN_STAGES = [
    f"""
       {COLOR_CYAN}-----
       |   |
           |
           |
           |
           |
    ---------\n{COLOR_RESET}
    """,
    f"""
       {COLOR_CYAN}-----
       |   |
       {COLOR_YELLOW}O{COLOR_CYAN}   |
           |
           |
           |
    ---------\n{COLOR_RESET}
    """,
    f"""
       {COLOR_CYAN}-----
       |   |
       {COLOR_YELLOW}O{COLOR_CYAN}   |
       {COLOR_YELLOW}|{COLOR_CYAN}   |
           |
           |
    ---------\n{COLOR_RESET}
    """,
    f"""
       {COLOR_CYAN}-----
       |   |
       {COLOR_YELLOW}O{COLOR_CYAN}   |
      {COLOR_YELLOW}/|{COLOR_CYAN}   |
           |
           |
    ---------\n{COLOR_RESET}
    """,
    f"""
       {COLOR_CYAN}-----
       |   |
       {COLOR_YELLOW}O{COLOR_CYAN}   |
      {COLOR_YELLOW}/|\\{COLOR_CYAN}  |
           |
           |
    ---------\n{COLOR_RESET}
    """,
    f"""
       {COLOR_CYAN}-----
       |   |
       {COLOR_YELLOW}O{COLOR_CYAN}   |
      {COLOR_YELLOW}/|\\{COLOR_CYAN}  |
      {COLOR_YELLOW}/{COLOR_CYAN}    |
           |
    ---------\n{COLOR_RESET}
    """,
    f"""
       {COLOR_CYAN}-----
       |   |
       {COLOR_RED}{COLOR_BOLD}O{COLOR_RESET}{COLOR_CYAN}   |
      {COLOR_RED}{COLOR_BOLD}/|\\{COLOR_RESET}{COLOR_CYAN}  |
      {COLOR_RED}{COLOR_BOLD}/ \\{COLOR_RESET}{COLOR_CYAN}  |
           |
    ---------\n{COLOR_RESET}
    """
]

# --- Helper Functions ---

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_words(filename):
    """Loads words from the file, organized by category."""
    categories = {}
    try:
        with open(filename, 'r') as f:
            current_category = None
            for line in f:
                line = line.strip().upper()
                if not line:
                    continue
                if line.startswith("[CATEGORY ") and line.endswith("]"):
                    current_category = line[len("[CATEGORY "):-1].strip()
                    categories[current_category] = []
                elif current_category and line and not line.startswith("#"): # Allow comments
                    if all(c in string.ascii_uppercase for c in line): # Basic word validation
                         categories[current_category].append(line)
                    else:
                        print(f"{COLOR_YELLOW}Warning: Skipping invalid word '{line}' in category '{current_category}'{COLOR_RESET}")

        # Validate loaded data
        if not categories:
            print(f"{COLOR_RED}Error: No categories found in {filename}. Exiting.{COLOR_RESET}")
            sys.exit(1)
        for category, words in categories.items():
            if not words:
                print(f"{COLOR_YELLOW}Warning: Category '{category}' has no valid words.{COLOR_RESET}")

        # Remove empty categories
        categories = {k: v for k, v in categories.items() if v}
        if not categories:
            print(f"{COLOR_RED}Error: No categories with valid words found in {filename}. Exiting.{COLOR_RESET}")
            sys.exit(1)

    except FileNotFoundError:
        print(f"{COLOR_RED}Error: Word file '{filename}' not found! Please create it. Exiting.{COLOR_RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{COLOR_RED}An error occurred while loading words: {e}{COLOR_RESET}")
        sys.exit(1)
    return categories

def load_high_scores(filename):
    """Loads high scores from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return [] # Return empty list if file doesn't exist or is invalid

def save_high_scores(filename, scores):
    """Saves high scores to a JSON file."""
    try:
        # Sort scores descending
        scores.sort(key=lambda x: x.get('score', 0), reverse=True)
        # Keep only top N scores
        scores = scores[:MAX_HIGH_SCORES]
        with open(filename, 'w') as f:
            json.dump(scores, f, indent=4)
    except IOError as e:
        print(f"{COLOR_RED}Error saving high scores: {e}{COLOR_RESET}")
    except Exception as e:
         print(f"{COLOR_RED}An unexpected error occurred saving scores: {e}{COLOR_RESET}")

def display_high_scores(scores):
    """Displays the formatted high scores."""
    clear_screen()
    print(f"{COLOR_BOLD}{COLOR_MAGENTA}--- High Scores ---{COLOR_RESET}\n")
    if not scores:
        print("No high scores recorded yet.")
    else:
        print(f"{COLOR_BOLD}{'Rank':<5} {'Name':<15} {'Score':<8} {'Category':<15} {'Difficulty'}{COLOR_RESET}")
        print("-" * 60)
        for i, entry in enumerate(scores):
             # Provide default values if keys are missing
            name = entry.get('name', 'N/A')
            score = entry.get('score', 0)
            category = entry.get('category', 'N/A')
            difficulty = entry.get('difficulty', 'N/A')
            print(f"{i+1:<5} {name:<15} {score:<8} {category:<15} {difficulty}")
    print("\n" + "-" * 60)
    input(f"\n{COLOR_YELLOW}Press Enter to return to the main menu...{COLOR_RESET}")

def select_category(categories):
    """Prompts the user to select a word category."""
    print(f"{COLOR_BLUE}Please select a category:{COLOR_RESET}")
    category_list = list(categories.keys())
    for i, category in enumerate(category_list):
        print(f"  {i + 1}. {category}")

    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(category_list):
                return category_list[choice - 1]
            else:
                print(f"{COLOR_RED}Invalid choice. Please enter a number between 1 and {len(category_list)}.{COLOR_RESET}")
        except ValueError:
            print(f"{COLOR_RED}Invalid input. Please enter a number.{COLOR_RESET}")

def select_difficulty():
    """Prompts the user to select a difficulty level."""
    print(f"\n{COLOR_BLUE}Select difficulty:{COLOR_RESET}")
    difficulty_options = list(DIFFICULTY_LEVELS.keys())
    for i, level in enumerate(difficulty_options):
        lives = DIFFICULTY_LEVELS[level]
        print(f"  {i + 1}. {level.capitalize()} ({lives} lives)")

    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(difficulty_options):
                return difficulty_options[choice - 1]
            else:
                print(f"{COLOR_RED}Invalid choice. Please enter a number between 1 and {len(difficulty_options)}.{COLOR_RESET}")
        except ValueError:
            print(f"{COLOR_RED}Invalid input. Please enter a number.{COLOR_RESET}")

def display_game_state(incorrect_guesses, word_progress, remaining_lives, score, hints_left, category, difficulty):
    """Displays the current state of the game."""
    clear_screen()
    stage_index = min(len(incorrect_guesses), len(HANGMAN_STAGES) - 1) # Prevent index out of bounds
    print(HANGMAN_STAGES[stage_index])
    print(f"Category: {COLOR_CYAN}{category}{COLOR_RESET} | Difficulty: {COLOR_CYAN}{difficulty.capitalize()}{COLOR_RESET}")
    print(f"Score: {COLOR_GREEN}{score}{COLOR_RESET}")
    print(f"\nWord:  {COLOR_BOLD}{' '.join(word_progress)}{COLOR_RESET}")
    print(f"\nIncorrect Guesses ({len(incorrect_guesses)}): {COLOR_RED}{', '.join(sorted(incorrect_guesses)) or 'None'}{COLOR_RESET}")
    print(f"Remaining Lives: {COLOR_YELLOW}{remaining_lives}{COLOR_RESET}")
    print(f"Hints Available: {COLOR_YELLOW}{hints_left}{COLOR_RESET}")
    print("-" * 40)

def get_player_action(already_guessed, hints_left):
    """Prompts the player for a letter guess or other actions (like 'hint')."""
    while True:
        action = input(f"Enter a letter guess, or type '{COLOR_YELLOW}hint{COLOR_RESET}' ({hints_left} left): ").upper()

        if action == "HINT":
            if hints_left > 0:
                return "HINT"
            else:
                print(f"{COLOR_RED}You have no hints remaining!{COLOR_RESET}")
        elif len(action) == 1 and action in string.ascii_uppercase:
            if action in already_guessed:
                print(f"{COLOR_YELLOW}You already guessed '{action}'. Try a different letter.{COLOR_RESET}")
            else:
                return action # Valid letter guess
        else:
            print(f"{COLOR_RED}Invalid input. Please enter a single letter or 'hint'.{COLOR_RESET}")


def provide_hint(secret_word, guessed_letters):
    """Finds an unguessed letter in the secret word to reveal as a hint."""
    unguessed_letters = [letter for letter in secret_word if letter not in guessed_letters]
    if unguessed_letters:
        return random.choice(unguessed_letters)
    return None # Should not happen if called correctly, but safeguard


# --- Main Game Logic ---

def play_hangman(categories):
    """Executes a single round of the advanced Hangman game."""
    category = select_category(categories)
    difficulty = select_difficulty()

    secret_word = random.choice(categories[category])
    word_letters = set(secret_word)
    guessed_letters = set()
    incorrect_guesses = set()
    word_progress = ["_"] * len(secret_word)

    max_lives = DIFFICULTY_LEVELS[difficulty]
    remaining_lives = max_lives
    hints_available = 1 if difficulty != "hard" else 0 # No hints on hard by default
    score = 0
    game_over = False
    message = ""

    clear_screen()
    print(f"{COLOR_GREEN}Starting new game!{COLOR_RESET}")
    print(f"Category: {category}, Difficulty: {difficulty.capitalize()}")
    print(f"Word has {len(secret_word)} letters. Good luck!")
    time.sleep(2.5) # Pause briefly

    # --- Game Loop ---
    while not game_over:
        display_game_state(incorrect_guesses, word_progress, remaining_lives, score, hints_available, category, difficulty)

        if message:
            print(message)
            message = "" # Clear message after displaying

        action = get_player_action(guessed_letters | incorrect_guesses, hints_available)

        if action == "HINT":
            hint_letter = provide_hint(secret_word, guessed_letters)
            if hint_letter:
                message = f"{COLOR_YELLOW}Hint: The letter '{hint_letter}' is in the word.{COLOR_RESET}"
                guessed_letters.add(hint_letter)
                hints_available -= 1
                remaining_lives -= 1 # Hint costs a life!
                score += SCORE_HINT_PENALTY

                # Update word progress for the hinted letter
                found_in_word = False
                for index, letter in enumerate(secret_word):
                    if letter == hint_letter:
                        word_progress[index] = hint_letter
                        found_in_word = True
                # This check shouldn't fail if provide_hint worked, but good practice
                if not found_in_word:
                     message = f"{COLOR_RED}Internal hint error occurred.{COLOR_RESET}" # Should not happen

            else: # Should only happen if word is already solved when hint is requested
                 message = f"{COLOR_YELLOW}No more letters to hint!{COLOR_RESET}"

        else: # It's a letter guess
            guess = action
            guessed_letters.add(guess)

            if guess in word_letters:
                message = f"{COLOR_GREEN}Correct! '{guess}' is in the word.{COLOR_RESET}"
                score += SCORE_CORRECT_GUESS
                # Update word_progress
                for index, letter in enumerate(secret_word):
                    if letter == guess:
                        word_progress[index] = guess
            else:
                message = f"{COLOR_RED}Incorrect. '{guess}' is not in the word.{COLOR_RESET}"
                incorrect_guesses.add(guess)
                remaining_lives -= 1
                score += SCORE_INCORRECT_GUESS

        # --- Check Win/Loss Conditions ---
        if "_" not in word_progress:
            score += SCORE_WIN_BONUS
            display_game_state(incorrect_guesses, word_progress, remaining_lives, score, hints_available, category, difficulty)
            print(f"\n{COLOR_BOLD}{COLOR_GREEN}*** Congratulations! You guessed the word: {secret_word} ***{COLOR_RESET}")
            print(f"Final Score: {score}")
            game_over = True
            return {"won": True, "score": score, "category": category, "difficulty": difficulty}

        elif remaining_lives <= 0:
            display_game_state(incorrect_guesses, word_progress, remaining_lives, score, hints_available, category, difficulty)
            print(f"\n{COLOR_BOLD}{COLOR_RED}--- Game Over ---{COLOR_RESET}")
            print(f"You ran out of lives. The word was: {COLOR_YELLOW}{secret_word}{COLOR_RESET}")
            print(f"Final Score: {score}")
            game_over = True
            return {"won": False, "score": score, "category": category, "difficulty": difficulty}

# --- Main Menu and Execution ---

def main():
    """Main function to run the game menu and logic."""
    try:
        all_categories = load_words(WORDS_FILENAME)
        high_scores = load_high_scores(HIGH_SCORES_FILENAME)
    except SystemExit: # Exit if loading failed
        return # Stop execution

    while True:
        clear_screen()
        print(f"{COLOR_BOLD}{COLOR_MAGENTA}=== Advanced Hangman ==={COLOR_RESET}")
        print("1. Play Game")
        print("2. View High Scores")
        print("3. Quit")
        choice = input("Enter your choice: ")

        if choice == '1':
            game_result = play_hangman(all_categories)
            if game_result["won"] or game_result["score"] > 0: # Save score if won or score > 0
                 if not any(hs['score'] < game_result['score'] for hs in high_scores) and len(high_scores) >= MAX_HIGH_SCORES:
                     print("\nGood game, but your score wasn't high enough for the leaderboard.")
                 else:
                    name = input("Enter your name for the high score list (leave blank to skip): ").strip()
                    if name:
                        high_scores.append({
                            "name": name,
                            "score": game_result["score"],
                            "category": game_result["category"],
                            "difficulty": game_result["difficulty"].capitalize()
                        })
                        save_high_scores(HIGH_SCORES_FILENAME, high_scores)
                        print(f"{COLOR_GREEN}High score saved!{COLOR_RESET}")
                    else:
                        print("High score not saved.")

            input(f"\n{COLOR_YELLOW}Press Enter to return to the main menu...{COLOR_RESET}")

        elif choice == '2':
            display_high_scores(high_scores)
        elif choice == '3':
            print(f"\n{COLOR_CYAN}Thanks for playing! Goodbye!{COLOR_RESET}")
            break
        else:
            print(f"{COLOR_RED}Invalid choice. Please try again.{COLOR_RESET}")
            time.sleep(1.5)


if __name__ == "__main__":
    main()
