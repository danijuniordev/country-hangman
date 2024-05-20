import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import time
import threading

# Access to Google Sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
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

    3 - View Scores.
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
    choice = input('Select an option:\n')
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
    stages = [  # Head, body, both arms, and both legs
        """
                      _____________        
           ████████  | oh, my neck!| 
           █      | /|_____________|
           █      O
           █     /|\
           █      |
           █     / \
           -
        """,
        # Head, body, both arms, and left leg
        """
                      _____________
           ████████  | Please,     |
           █      | /| Last chance!|
           █      O  |_____________|
           █     /|\
           █      |
           █     / 
           -
        """,
        # Head, body, and both arms
        """
           ████████
           █      |
           █      O
           █     /|\
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
    try:
        score_sheet = client.open('hangman-words').worksheet('Scores')
    except gspread.exceptions.WorksheetNotFound:
        sheet = client.open('hangman-words')
        score_sheet = sheet.add_worksheet(title='Scores', rows='100', cols='3')
        score_sheet.append_row(['Name', 'Score', 'Timestamp'])

    score_sheet.append_row([name, score, time.strftime("%Y-%m-%d %H:%M:%S")])

def view_scores():
    clear_terminal()
    try:
        score_sheet = client.open('hangman-words').worksheet('Scores')
        scores = score_sheet.get_all_records()

        if not scores:
            print("No scores available.")
        else:
            scores.sort(key=lambda x: x['Score'], reverse=True)
            print("High Scores:\n")
            for idx, record in enumerate(scores):
                print(f"{idx+1}. {record['Name']} - {record['Score']} - {record['Timestamp']}")
    except gspread.exceptions.WorksheetNotFound:
        print("No scores available.")

    bottom_input()

def start_game():
    '''
    start the game
    '''
    name = input("Enter your name: ")
    word = get_random_word()
    guessed_letters = []
    guessed_word = ['_'] * len(word)
    tries = 6
    score = 0
    start_time = time.time()

    clear_terminal()
    print("Welcome to the Hangman Game!")
    print(draw_hangman(tries))
    print("Guess the country:")
    print(" ".join(guessed_word))
    print("You have 1 minute to guess.")

    while tries > 0 and '_' in guessed_word:
        if time.time() - start_time > 60:
            print(fail_game)
            print("Time's up! You couldn't guess the word in time.")
            print("The word was:", word)
            store_score(name, score)
            return
        guess = input("Enter a letter or guess the complete word:\n").lower()

        if guess == 'hint':
            if score >= 15:
                hint = get_hint(word, guessed_word, guessed_letters)
                if hint:
                    score -= 15
                    print(f"Here's your hint! The letter '{hint}' is in the word.")
                    for i in range(len(word)):
                        if word[i] == hint:
                            guessed_word[i] = hint
                else:
                    print("No hints available.")
            else:
                print("Not enough points for a hint! You need at least 15 points.")

        if len(guess) == 1 and guess.isalpha():
            if guess in guessed_letters:
                print(draw_hangman(tries))
                print("You've already tried that letter. Try another one.")
                continue
            guessed_letters.append(guess)

            if guess in word:
                print("Correct letter!")
                score += 10
                for i in range(len(word)):
                    if word[i] == guess:
                        guessed_word[i] = guess
                print(draw_hangman(tries))
            else:
                print("Wrong letter!")
                score -= 5
                tries -= 1
                print(draw_hangman(tries))

            print("Letters tried:", ", ".join(guessed_letters))
            print(" ".join(guessed_word))
        elif len(guess) == len(word) and guess.isalpha():
            if guess == word:
                score += 50
                print(win_game)
                print("You guessed the word:", word)
                print("Your score:", score)
                store_score(name, score)
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
        store_score(name, score)
    else:
        print(fail_game)
        print("You've been hanged! The word was:", word)
        print("Your score:", score)
        store_score(name, score)

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