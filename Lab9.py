import json
import random
import os
import sys
import re

# Part 1 ============================================================

HOW_MANY_BOOK = 3
LINE = 128
PAGE = 64
pages = {}
page_number=0
line_window = {}
line_number = 0
char_window = []

# Part 2 ============================================================
# 1. Cleaning Text
def clean_line(line):
    return line.strip().replace( '-', '' ) + ' '  # Adding a space instead of a newline.
# 2. Reading a Book File
def read_book(file_path):
    global char_window
    with open(file_path, 'r', encoding='utf-8-sig') as fp:
        for line in fp:
            line = clean_line(line)
            if line.strip():
                for c in line:
                    process_char(c)
    if len(char_window) > 0:
        add_line()
    if len(line_window) > 0:
        add_page()

# Part 3 ============================================================
# 1. Buffering/Windowing

def process_char(char):
    global char_window
    char_window.append(char)
    if len(char_window) == LINE:
        add_line()


def add_line():
    global char_window, line_number
    line_number += 1
    process_page( ''.join(char_window), line_number )
    char_window.clear()

# 2. Buffering/Windowing

def process_page(line, line_num):
    global line_window, pages, page_number
    line_window[line_num] = line
    if len(line_window) == PAGE:
        add_page()


def add_page():
    global line_number, line_window, pages, page_number
    page_number += 1
    pages[page_number] = dict(line_window)
    line_window.clear()
    line_number = 0

# Part 4 ============================================================
# 1. Reading Multiple Books
def process_books(*paths):
    for path in paths:
        read_book( path )

# 2. Generalization Discussion: What would be some pros and cons of different ways to combine books
# for greater randomness in your one-time-pad?
# I guess you are spending more processing time the more you mix it up, but you get more security.
# It's the classic security/conveiniece tradeoff

# Part 5 ============================================================
# 1. Generating the code book
def generate_code_book():
    global pages
    code_book = {}
    for page, lines in pages.items():
        for num, line in lines.items():
            for pos, char in enumerate(line):
                code_book.setdefault(char, []).append(f'{page}-{num}-{pos}')
    return code_book

# 2. Saving and loading the codebook

def save(file_path, book):
    with open(file_path, 'w') as fp:
        # json.dump(book, fp, indent=4)
        json.dump(book, fp)


def load(file_path, *key_books, reverse=False):
    if os.path.exists(file_path):
        with open(file_path, 'r') as fp:
            return json.load(fp)
    else:
        process_books(*key_books)
        if reverse:
            save(file_path, pages)
            return pages
        else:
            code_book = generate_code_book()
            save(file_path, code_book)
            return code_book

# Part 6 ============================================================
# 1. Encrypting a Message

def encrypt(code_book, message):
    cipher_text = []
    for char in message:
        index = random.randint(0, len(code_book[char]) - 1)
        cipher_text.append(code_book[char].pop(index))
    return '-'.join(cipher_text)

# 2. Decrypting a Message

def decrypt(rev_code_book, ciphertext):
    plaintext = []
    for cc in re.findall(r'\d+-\d+-\d+', ciphertext):
        page, line, char = cc.split('-')
        plaintext.append(
            rev_code_book[page][line][int(char)])
    return ''.join(plaintext)

# Part 7 ============================================================
# 1. Creating a user interface
def main_menu():
    print("""1). Encrypt
2). Decrypt
3). Quit
""")
    return int(input("Make a selection [1,2,3]: "))


def main():
    key_books = ('books/War_and_Peace.txt', 'books/Moby_Dick.txt', 'books/Dracula.txt')
    code_book_path = 'code_books/dmdwp.txt'
    rev_code_book_path = 'code_books/dmdwp_r.txt'
    while True:
        try:
            choice = main_menu()
            match choice:
                case 1:
                    code_book = load(code_book_path, *key_books)
                    message = input("Please enter your secret message: ")
                    print(encrypt(code_book, message))
                    continue
                case 2:
                    rev_code_book = load(rev_code_book_path, *key_books, reverse=True)
                    message = input("Please enter your cipher text: ")
                    print(decrypt(rev_code_book, message))
                    continue
                case 3:
                    sys.exit(0)
        except ValueError:
            print("Improper selection.")


if __name__ == '__main__':
    main()

# Part 8 ============================================================