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

    bottom_input()

def bottom_input():
    '''
    Prints a line of '-' and waits for user input before returning to the menu.
    '''
    print('-' * 80)
    input('Press ENTER to return to the menu...')
    main()

main()