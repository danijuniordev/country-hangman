import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import time

# Access to Google Sheet
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)
sheet = client.open('hangman-words').sheet1

# Colour
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

game_start = '''
      ██████████████████████████████████████████████████████████████████████
      █                   Welcome to the hangman challenge!                █
      █                                                                    █
      █   1 - Start Game.                                                  █
      █                                                                    █
      █   2 - Introduction.                                                █
      █                                                                    █
      █   3 - View Scores.                                                 █
      █                                                                    █
      ██████████████████████████████████████████████████████████████████████
'''
win_game = fr"""
{GREEN}
                                 _         _       _   _                   _
                                | |       | |     | | (_)                 | |
  ___ ___  _ __   __ _ _ __ __ _| |_ _   _| | __ _| |_ _  ___  _ __  ___  | |
 / __/ _ \| '_ \ / _` | '__/ _` | __| | | | |/ _` | __| |/ _ \| '_ \/ __| | |
| (_| (_) | | | | (_| | | | (_| | |_| |_| | | (_| | |_| | (_) | | | \___  |_|
 \___\___/|_| |_|\__, |_|  \__,_|\__|\__,_|_|\__,_|\__|_|\___/|_| |_|___| (_)
                  __/ |
                 |___/
{RESET}
"""

fail_game = fr"""
{RED}
   _____                                                             _
  / ____|                                                           | |
 | |  __   __ _   _ __ ___     ___      ___   __   __   ___   _ __  | |
 | | |_ | / _  | |  _   _ \   / _ \    / _ \  \ \ / /  / _ \ |  __| | |
 | |__| || (_| | | | | | | | |  __/   | (_) |  \ V /  |  __/ | |    |_|
  \_____| \__,_| |_| |_| |_|  \___|    \___/    \_/    \___| |_|    (_)
{RESET}
"""

times_over = fr"""
{RED}
  _______   _                                              _
 |__   __| (_)                                            | |
    | |     _   _ __ ___     ___   ___     _   _   _ __   | |
    | |    | | | '_ ` _ \   / _ \ / __|   | | | | | '_ \  | |
    | |    | | | | | | | | |  __/ \__ \   | |_| | | |_) | |_|
    |_|    |_| |_| |_| |_|  \___| |___/    \__,_| | .__/  (_)
                                                  | |
                                                  |_|
{RESET}
"""

# Variables
FEEDBACK_TIME = 2


def clear_terminal():
    '''
    Clears the terminal.
    '''
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    '''
    Main manu, where the users select an option
    '''
    clear_terminal()
    print(game_start)
    choice = input('Select an option: ')
    valid_choices = ['1', '2', '3']

    if choice not in valid_choices:
        print('Invalid selection, try again.')

        time.sleep(FEEDBACK_TIME)
        main()
    elif choice == '1':
        start_game()
    elif choice == '2':
        instructions()
    elif choice == '3':
        view_scores()


def bottom_input():
    '''
    Prints a line of '-' and waits for user input before returning to the menu.
    '''
    print("")
    input(f'Press {BLUE}ENTER{RESET} to return to the menu...')
    main()


def instructions():
    '''
    Print game instructions.
    '''
    clear_terminal()
    print('Welcome to the challenging world of Global Hangman!\n')
    print("Get ready to test your geographical knowledge across the game.")
    print('Guess the country before the hangman is fully drawn.')
    print('Each incorrect letter choice brings you closer to the dead!\n')
    print('You have 1 minute to guess the country.')
    print(f'For each correct letter, you earn {GREEN}10 points{RESET}.')
    print(f'For each incorrect letter, you lose {RED}5 points{RESET}.')
    print(f'After earning {GREEN}15 points{RESET}.')
    print(f'You can ask for a hint by typing {BLUE}"hint"{RESET}.')

    bottom_input()


def get_random_word():
    '''
    Get a random word from the google sheet
    '''
    words = sheet.col_values(1)
    return random.choice(words).lower()


def draw_hangman(tries):
    '''
    Draw the body each time when the user guess an incorrect letter
    '''
    stages = [  # Head, body, both arms, and both legs
        """
                      ______________
                     |    Nooo!!    |
           ████████  |   my neck!   |
           █      | /|______________|
           █      O
           █     /|\\
           █      |
           █     / \\
           -
        """,
        # Head, body, both arms, and left leg
        """
                      ______________
                     |              |
           ████████  |    Please,   |
           █      | /| Last chance! |
           █      O  |______________|
           █     /|\\
           █      |
           █     /
           -
        """,
        # Head, body, and both arms
        """
           ████████
           █      |
           █      O
           █     /|\\
           █      |
           █
           -
        """,
        # Head, body, and left arm
        """
           ████████
           █      |
           █      O
           █     /|
           █      |
           █
           -
        """,
        # Head and body
        """
           ████████
           █      |
           █      O
           █      |
           █      |
           █
           -
        """,
        # Head
        """
           ████████
           █      |
           █      O
           █
           █
           █
           -
        """,
        # Empty
        """
           ████████
           █      |
           █
           █
           █
           █
           -
        """
    ]
    return stages[tries]


def store_score(name, score):
    '''
    Used to store the scores on the googlesheet
    '''
    try:
        score_sheet = client.open('hangman-words').worksheet('Scores')
    except gspread.exceptions.WorksheetNotFound:
        sheet = client.open('hangman-words')
        score_sheet = sheet.add_worksheet(title='Scores', rows='100', cols='3')
        score_sheet.append_row(['Name', 'Score'])

    score_sheet.append_row([name, score])


def view_scores():
    '''
    Used to display the scores
    '''
    clear_terminal()
    try:
        score_sheet = client.open('hangman-words').worksheet('Scores')
        scores = score_sheet.get_all_records()

        if not scores:
            print("No scores available.")
        else:
            scores.sort(key=lambda x: x['Score'], reverse=True)
            print("High Scores:")
            for idx, record in enumerate(scores):
                print("-"*50)
                print(f"{idx+1}. {record['Name']} - {record['Score']}")
    except gspread.exceptions.WorksheetNotFound:
        print("No scores available.")

    bottom_input()


def start_game():
    '''
    Start the game
    '''
    print("")
    name = ""
    while not name.strip():
        name = input("Enter your name: ").strip()
    word = get_random_word()
    guessed_letters = []
    guessed_word = ['_'] * len(word)
    tries = 6
    score = 0
    start_time = time.time()

    clear_terminal()
    print("Welcome to the Hangman Game!\n")
    print(draw_hangman(tries))
    print("Guess the country:\n")
    print(" ".join(guessed_word))
    print("\nYou have 1 minute to guess.\n")
    print(f"After earning {RED}15 points{RESET}\n")
    print(f"You can ask for a hint by typing {BLUE}'hint'{RESET}.")

    while tries > 0 and '_' in guessed_word:
        if time.time() - start_time > 60:
            clear_terminal()
            print(times_over)
            print(f"The word was:{BLUE}{word}{RESET}")
            store_score(name, score)
            bottom_input()

        guess = input("\nEnter a letter or guess the complete word: ").lower()

        if guess == 'hint':
            if score >= 15:
                hint = get_hint(word, guessed_word, guessed_letters)
                if hint:
                    score -= 15
                    print(f"\nHere's your hint!\n")
                    print(f"The letter {BLUE}'{hint}'{RESET}.\n")
                    for i in range(len(word)):
                        if word[i] == hint:
                            guessed_word[i] = hint
                else:
                    print("No hints available.")
                continue
            else:
                print("\nNot enough points for a hint! You need 15 points.")
                continue

        if len(guess) == 1 and guess.isalpha():
            if guess in guessed_letters:
                clear_terminal()
                print(draw_hangman(tries))
                for i in range(len(word)):
                    if word[i] == guess:
                        guessed_word[i] = guess
                print("Letters tried:", ", ".join(guessed_letters))
                print(" ".join(guessed_word))
                print("\nYou've already tried that letter. Try another one.")
                continue
            guessed_letters.append(guess)

            if guess in word:
                clear_terminal()
                score += 10
                for i in range(len(word)):
                    if word[i] == guess:
                        guessed_word[i] = guess
                print(draw_hangman(tries))
                print(f"{GREEN}Correct letter!\n{RESET}")
            else:
                clear_terminal()
                score -= 5
                tries -= 1
                print(draw_hangman(tries))
                print(f"{RED}Wrong letter!\n{RESET}")

            print("Letters tried:", ", ".join(guessed_letters))
            print(" ".join(guessed_word))
        elif len(guess) == len(word) and guess.isalpha():
            if guess == word:
                score += 50
                clear_terminal()
                print(win_game)
                print(f"You guessed the word: {GREEN}{word}{RESET}\n")
                print(f"Your score:{BLUE}{score}{RESET}")
                store_score(name, score)
                bottom_input()
            else:
                clear_terminal()
                print(fail_game)
                print(f"Incorrect! The word was not: {RED}{guess}{RESET}\n")
                print(f"The word was: {BLUE}{word}{RESET}\n")
                print(f"Your score:{BLUE}{score}{RESET}\n")
                store_score(name, score)
                bottom_input()
        else:
            print("Invalid input.\n")
            print("Please enter either one letter or guess the complete word.")

    if '_' not in guessed_word:
        clear_terminal()
        print(win_game)
        print(f"You guessed the word: {GREEN}{word}{RESET}\n")
        print(f"Your score:{BLUE}{score}{RESET}")
        store_score(name, score)
        bottom_input()
    else:
        clear_terminal()
        print(fail_game)
        print(f"You've been hanged! The word was: {BLUE}{word}{RESET}\n")
        print(f"Your score:{BLUE}{score}{RESET}")
        store_score(name, score)
        bottom_input()


def get_hint(word, guessed_word, guessed_letters):
    '''
    Provide a hint by revealing an unrevealed letter in the word.
    '''
    for letter in word:
        if letter not in guessed_word and letter not in guessed_letters:
            return letter
    return None


if __name__ == "__main__":
    main()
