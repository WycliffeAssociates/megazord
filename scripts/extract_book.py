import sys
import os
import re
import json
from shutil import copyfile

class Book(object):
    def __init__(self, folder_name):
        super(Book, self).__init__()
        self.parse_folder_name(folder_name)

    def parse_folder_name(self, folder_name):
        self.path = folder_name
        name_parts = folder_name.split('_')
        self.language = name_parts[0]
        self.code = name_parts[1].upper()
        self.file = name_parts[2]
        self.type = name_parts[3]
        self.checking_level = name_parts[4]

    def rename(self, sort):
        sort_string = str(sort)
        if len(sort_string) < 2:
            sort_string = '0' + sort_string

        self.new_name = sort_string + '-' + self.code + '.usfm'

class BCSBook(object):
    def __init__(self, filename):
        super(Book, self).__init__()
        self.parse_filename(filename)

    def parse_folder_name(self, filename):
        self.path = filename
        self.new_name = re.sub(r'_3.SFM', '', re.sub(r'L119_', '', filename))

def extract_book(source_folder, convention):
    with open('data/verses.json') as verses_file:
        verses = json.load(verses_file)

    if (convention === 'rodrigo'):
        extract_rodrigo_style(source_folder, verses)
    else if (convention === 'bcs'):
        extract_bcs_style(source_folder, verses)

def extract_rodrigo_style(source_folder, verses):
    for book_folder in os.listdir(source_folder):
        book = Book(book_folder)
        path_to_book_folder = os.path.join(source_folder, book_folder)

        for f in os.listdir(path_to_book_folder):
            if '.usfm' in f:
                path_to_source_file = os.path.join(source_folder, book_folder, f)
                path_to_target_folder = os.path.join('results', book.language + '_' + book.type)

                if not os.path.isdir(path_to_target_folder):
                    os.makedirs(path_to_target_folder)

                book.rename(verses.get(book.code).get('sort'))

                path_to_target_file = os.path.join(path_to_target_folder, book.new_name)
                copyfile(path_to_source_file, path_to_target_file)

def extract_bcs_style(source_folder, verses):
    pass


if __name__ == "__main__":
    source_folder = sys.argv[1]
    convention = sys.argv[2]
    extract_book(source_folder, convention)

    print "\nDone."
