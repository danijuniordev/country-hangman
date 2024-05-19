import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import time
import threading

## access to googlesheet
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)
sheet = client.open('hangman-words').sheet1

game_start = '''
    █     █   ████████   ██      █  ███████    ██       ██   ████████   ██      █ 
    █     █   █      █   █ █     █  █          █ █     █ █   █      █   █ █     █
    █     █   █      █   █  █    █  █          █  █   █  █   █      █   █  █    █
    ███████   ████████   █   █   █  █   ████   █   █ █   █   ████████   █   █   █
    █     █   █      █   █    █  █  █      █   █    █    █   █      █   █    █  █
    █     █   █      █   █     █ █  █      █   █         █   █      █   █     █ █ 
    █     █   █      █   █      ██  ████████   █         █   █      █   █      ██

    1 - Start Game.

    2 - Introduction.
'''
win_game = """ 
    █        █   ████████   █          █              █████       █████████   ██      █   ████████  
    █        █   █          █          █              █     █     █       █   █ █     █   █ 
    █        █   █          █          █              █       █   █       █   █  █    █   █
    █   ██   █   █████      █          █              █       █   █       █   █   █   █   █████
    █  █  █  █   █          █          █              █      █    █       █   █    █  █   █
    █ █    █ █   █          █          █              █    █      █       █   █     █ █   █
    ██      ██   ████████   ████████   ████████       █████       █████████   █      ██   ████████ 
"""

fail_game = """ 
    ████████   ████████   █   █
    █          █      █   █   █
    █          █      █   █   █
    ██████     ████████   █   █
    █          █      █   █   █
    █          █      █   █   █
    █          █      █   █   ████████
"""
## Variables
FEEDBACK_TIME = 2

def clear_terminal():
    '''
    Clears the terminal.
    '''

    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_terminal()
    print(game_start)
    choice = input('Select an option: ')
    valid_choices = ['1', '2']

    if choice not in valid_choices:
        print('Invalid selection, try again.')
        time.sleep(FEEDBACK_TIME)
        main()
    elif choice == '1':
        start_game()
    elif choice == '2':
        instructions()

def instructions():
    '''
    Print game instructions.
    '''
    clear_terminal()
    print('Welcome to the challenging world of Global Hangman!\n')
    print('Get ready to test your geographical knowledge as you journey across the game.')
    print('In this thrilling game, your objective is to guess the secret country before the hangman is fully drawn.')
    print('Each incorrect letter choice brings you closer to the hangman is fate, so choose wisely!\n')
    print('You have 1 minute to guess the word')

    bottom_input()

def bottom_input():
    '''
    Prints a line of '-' and waits for user input before returning to the menu.
    '''
    print('-' * 100)
    input('Press ENTER to return to the menu...')
    main()

def get_random_word():
    words = sheet.col_values(1)
    return random.choice(words).lower()

def draw_hangman(tries):
    stages = [  # Head, body, both arm and both lag
        """
           --------
           |      |
           |      O
           |     \|/
           |      |
           |     / \\
           -
        """,
        # Head, body, both arm and left lag
        """
           --------
           |      |
           |      O
           |     \|/
           |      |
           |     / 
           -
        """,
        # Head, body and both arm
        """
           --------
           |      |
           |      O
           |     \|/
           |      |
           |      
           -
        """,
        # Head, body and left arm
        """
           --------
           |      |
           |      O
           |     \|
           |      |
           |     
           -
        """,
        # Head, body
        """
           --------
           |      |
           |      O
           |      |
           |      |
           |     
           -
        """,
        # Head
        """
           --------
           |      |
           |      O
           |    
           |      
           |     
           -
        """,
        # Empyt
        """
           --------
           |      |
           |      
           |    
           |      
           |     
           -
        """
    ]
    return stages[tries]

def start_game():
    word = get_random_word()
    guessed_letters = []
    guessed_word = ['_'] * len(word)
    tries = 7
    score = 0
    start_time = time.time()

    print("Welcome to the Hangman Game!")
    print("Guess the word:")
    print(" ".join(guessed_word))
    print("You have 1 minute to guess.")

    clear_terminal()

    while tries > 0 and '_' in guessed_word:
        if time.time() - start_time > 60:
            print(fail_game)
            print("Time's up! You couldn't guess the word in time.")
            print("The word was:", word)
            return
        guess = input("Enter a letter or guess the complete word: ").lower()

        if len(guess) == 1 and guess.isalpha():
            if guess in guessed_letters:
                print("You've already tried that letter. Try another one.")
                continue
            guessed_letters.append(guess)

            if guess in word:
                print("Correct letter!")
                score += 10
                for i in range(len(word)):
                    if word[i] == guess:
                        guessed_word[i] = guess
            else:
                print("Wrong letter!")
                score -= 5
                tries -= 1
                print(draw_hangman(tries))

            print("Letters tried:", ", ".join(guessed_letters))
            print(" ".join(guessed_word))
        elif len(guess) == len(word) and guess.isalpha():
            if guess == word:
                print(win_game)
                score += 50
                print("You guessed the word:", word)
                print("Your score:", score)
                return
            else:
                print(fail_game)
                print("Incorrect guess! The word was not:", guess)
                print("You've been hanged! The word was:", word)
                print("Your score:", score)
                return
        else:
            print("Invalid input. Please enter either one letter or guess the complete word.")

    if '_' not in guessed_word:
        print(win_game)
        print("You guessed the word:", word)
        print("Your score:", score)
    else:
        print(fail_game)
        print("You've been hanged! The word was:", word)
        print("Your score:", score)

if __name__ == "__main__":
    main()