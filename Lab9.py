import json
import random
import os
import sys
import re
from itertools import chain # For part 8 - a nifty little doodad Claude told me about

# Part 1 ============================================================

# HOW_MANY_BOOK = 3
LINE = 128
PAGE = 64
# pages = {}
# page_number=0
# line_window = {}
# line_number = 0
# char_window = []

# Part 2 ============================================================
# 1. Cleaning Text
# def clean_line(line):
#     return line.strip().replace( '-', '' ) + ' '  # Adding a space instead of a newline.
# 2. Reading a Book File
# def read_book(file_path):
#     global char_window
#     with open(file_path, 'r', encoding='utf-8-sig') as fp:
#         for line in fp:
#             line = clean_line(line)
#             if line.strip():
#                 for c in line:
#                     process_char(c)
#     if len(char_window) > 0:
#         add_line()
#     if len(line_window) > 0:
#         add_page()

# Part 3 ============================================================
# 1. Buffering/Windowing

# def process_char(char):
#     global char_window
#     char_window.append(char)
#     if len(char_window) == LINE:
#         add_line()
#
#
# def add_line():
#     global char_window, line_number
#     line_number += 1
#     process_page( ''.join(char_window), line_number )
#     char_window.clear()

# 2. Buffering/Windowing

# def process_page(line, line_num):
#     global line_window, pages, page_number
#     line_window[line_num] = line
#     if len(line_window) == PAGE:
#         add_page()
#
#
# def add_page():
#     global line_number, line_window, pages, page_number
#     page_number += 1
#     pages[page_number] = dict(line_window)
#     line_window.clear()
#     line_number = 0

# Part 4 ============================================================
# 1. Reading Multiple Books
# def process_books(*paths):
#     global page_number
#     # Start clean so a second build in one session doesn't append to the first.
#     pages.clear()
#     page_number = 0
#     for path in paths:
#         read_book( path )

# 2. Generalization Discussion: What would be some pros and cons of different ways to combine books
# for greater randomness in your one-time-pad?
# I guess you are spending more processing time the more you mix it up, but you get more security.
# It's the classic security/conveiniece tradeoff

# Part 5 ============================================================
# 1. Generating the code book
# def generate_code_book():
#     global pages
#     code_book = {}
#     for page, lines in pages.items():
#         for num, line in lines.items():
#             for pos, char in enumerate(line):
#                 code_book.setdefault(char, []).append(f'{page}-{num}-{pos}')
#     return code_book

# 2. Saving and loading the codebook

# def save(file_path, book):
#     with open(file_path, 'w') as fp:
#         # json.dump(book, fp, indent=4)
#         json.dump(book, fp)
#
#
# def load(file_path, *key_books, reverse=False):
#     if not os.path.exists(file_path):
#         process_books(*key_books)
#         save(file_path, pages if reverse else generate_code_book())
#     # Always read from disk: JSON turns int keys into strings, and decrypt expects strings.
#     with open(file_path, 'r') as fp:
#         return json.load(fp)

# Part 6 ============================================================
# 1. Encrypting a Message

# def encrypt(code_book, message):
#     cipher_text = []
#     for char in message:
#         index = random.randint(0, len(code_book[char]) - 1)
#         cipher_text.append(code_book[char].pop(index))
#     return '-'.join(cipher_text)

# 2. Decrypting a Message

# def decrypt(rev_code_book, ciphertext):
#     plaintext = []
#     for cc in re.findall(r'\d+-\d+-\d+', ciphertext):
#         page, line, char = cc.split('-')
#         plaintext.append(
#             rev_code_book[page][line][int(char)])
#     return ''.join(plaintext)

# Part 7 ============================================================
# 1. Creating a user interface
def main_menu():
    print("""1). Encrypt
2). Decrypt
3). Quit
""")
    return int(input("Make a selection [1,2,3]: "))


def select_code_book(key_books, code_books):
    subchoice = input("Would you like to use sequential (1) or interleaved (2) book combination: ")
    match subchoice: # input() returns a string, so these cases are strings too
        case '1':
            path, combine = 'code_books/sequential.json', sequential
        case '2':
            path, combine = 'code_books/interleaved.json', interleaved
        case _:
            print("Improper selection.")
            return None
    # Keep each code book for the whole session, so positions used by encrypt stay used
    if subchoice not in code_books:
        code_books[subchoice] = CodeBook.load_or_build(path, key_books, combine)
    return code_books[subchoice]


def main():
    key_books = [Book('books/War_and_Peace.txt'), Book('books/Moby_Dick.txt'), Book('books/Dracula.txt')]
    code_books = {}
    os.makedirs('code_books', exist_ok=True) # The folder is gitignored, so a fresh clone won't have it
    while True:
        try:
            choice = main_menu()
        except ValueError:
            print("Improper selection.")
            continue
        match choice:
            case 1:
                code_book = select_code_book(key_books, code_books)
                if code_book is None:
                    continue
                message = input("Please enter your secret message: ")
                try:
                    print(code_book.encrypt(message))
                except (KeyError, ValueError): # Character isn't in the books, or all its positions are used
                    print("That message can't be encrypted with this code book.")
            case 2:
                code_book = select_code_book(key_books, code_books)
                if code_book is None:
                    continue
                message = input("Please enter your cipher text: ")
                try:
                    print(code_book.decrypt(message))
                except (KeyError, IndexError): # A position that doesn't exist in this code book
                    print("That cipher text doesn't match this code book.")
            case 3:
                sys.exit(0)
            case _:
                print("Improper selection.")



# Part 8 ============================================================

# Objects yo!

class Book:
    def __init__(self, path):
        self.path = path

    def __iter__(self): # Make a book an iterable so it's useful, yields a line
        with open(self.path, encoding='utf-8-sig') as book:
            for line in book:
                line = line.strip().replace('-', '')
                if line: # Only add the space if there is a line
                    yield line + ' '

def sequential(books):
    return chain.from_iterable(books) # Chain is cool, it stacks iterables so we can use multiple books in sequence

def interleaved(books):
    readers = [iter(book) for book in books] # Makes a list of books, and their lines yield from iterable
    while readers: # While we still have books
        for reader in list(readers): # Loop through the books, adding a line
            try:
                yield next(reader)
            except StopIteration: # If a book ends, we need to remove it from the list
                readers.remove(reader)

class CodeBook:
    def __init__(self, pages):
        self.pages = pages
        self.positions = self._index(pages)

    @staticmethod
    def _index(pages): # I learned that the leading underscore is a 'private' method naming convention
        positions = {}
        for page, lines in pages.items():
            for num, line in lines.items():
                for pos, char in enumerate(line):
                    positions.setdefault(char, []).append(f'{page}-{num}-{pos}')
        return positions

    @classmethod
    def from_books(cls, books, combine=sequential):
        pages = {}
        text = ''.join(combine(books))
        all_lines = [text[i:i + LINE] for i in range(0, len(text), LINE)]
        for page_num, start in enumerate(range(0, len(all_lines), PAGE), start=1):
            chunk = all_lines[start:start + PAGE]

            page = {}
            for line_num, line in enumerate(chunk, start=1):
                page[str(line_num)] = line

            pages[str(page_num)] = page
        return cls(pages)

    @classmethod
    def load(cls, path):
        with open(path) as fp:
            return cls(json.load(fp))

    def save(self, path):
        with open(path, 'w') as fp:
            json.dump(self.pages, fp)

    def encrypt(self, message):
        cipher_text = []
        for char in message:
            index = random.randint(0, len(self.positions[char] ) -1)
            cipher_text.append(self.positions[char].pop(index))
        return '-'.join(cipher_text)

    def decrypt(self, ciphertext):
        plaintext = []
        for cc in re.findall(r'\d+-\d+-\d+', ciphertext):
            page, line, char = cc.split('-')
            plaintext.append(
                self.pages[page][line][int(char)])
        return ''.join(plaintext)

    @classmethod
    def load_or_build(cls, path, books, combine=sequential):
        if os.path.exists(path):
            return cls.load(path)
        code_book = cls.from_books(books, combine)
        code_book.save(path)
        return code_book





if __name__ == '__main__':
    main()
