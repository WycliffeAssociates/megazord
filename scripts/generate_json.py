import sys
import os
import re
import json
from shutil import copyfile


book_data = None


class Language(object):
    def __init__(self, folder_name):
        super(Language, self).__init__()
        self.code = self._get_code(folder_name)
        self.contents = []

    def _get_code(self, folder_name):
        return folder_name.split('_')[0]

    def add_content(self, content):
        self.contents.append(content)

    def to_dict(self):
        dictionary = self.__dict__
        dictionary['contents'] = [content.to_dict() for content in self.contents]
        return dictionary


class Content(object):
    def __init__(self, folder_name):
        super(Content, self).__init__()
        self.code = self._get_code(folder_name)
        self.name = self._map_code_to_name()
        self.subject = self._map_code_to_subject()
        self.links = []
        self.subcontents = []

    def _get_code(self, folder_name):
        return folder_name.split('_')[1]

    def _map_code_to_name(self):
        mapping = {
            'ulb': 'Unlocked Literal Bible',
            'udb': 'Unlocked Dynamic Bible',
            'obs': 'Open Bible Stories',
        }
        return mapping.get(self.code, 'Unknown')

    def _map_code_to_subject(self):
        mapping = {
            'ulb': 'Bible',
            'udb': 'Bible',
            'obs': 'Bible stories',
        }
        return mapping.get(self.code, 'Unknown')

    def add_link(self, link):
        self.links.append(link)

    def add_subcontent(self, subcontent):
        self.subcontents.append(subcontent)

    def to_dict(self):
        dictionary = self.__dict__
        dictionary['links'] = [link.to_dict() for link in self.links]
        dictionary['subcontents'] = [subcontent.to_dict() for subcontent in self.subcontents]
        return dictionary


class Subcontent(object):
    # File name is expected to be 'XX-XXX.usfm'. Example: '01-GEN.usfm'
    def __init__(self, file_name):
        super(Subcontent, self).__init__()
        self.code = self._get_code(file_name)
        self.sort = self._get_sort(file_name)
        self.name = self._get_name()
        self.category = self._get_category()
        self.links = []

    def _get_code(self, file_name):
        return file_name.replace('.usfm', '').split('-')[1].lower()

    def _get_sort(self, file_name):
        return int(file_name.replace('.usfm', '').split('-')[0])

    def _get_category(self):
        return 'bible-' + book_data[self.code].get('anth') if self.code in book_data.keys() else 'Unknown'

    def _get_name(self):
        return book_data[self.code].get('name') if self.code in book_data.keys() else 'Unknown'

    def add_link(self, link):
        self.links.append(link)

    def to_dict(self):
        dictionary = self.__dict__
        dictionary['links'] = [link.to_dict() for link in self.links]
        return dictionary


class Link(object):

    def __init__(self, path_to_file):
        super(Link, self).__init__()
        self.url = self._get_url(path_to_file)
        self.format = self._get_format(path_to_file)
        self.zipContent = self._get_zip_content()
        self.quality = ''

    def _get_url(self, path_to_file):
        url = 'https://s3.us-east-2.amazonaws.com/biel/translations' + path_to_file.replace('results', '')
        return url

    def _get_format(self, path_to_file):
        file_name = os.path.basename(path_to_file)
        _, ext = os.path.splitext(file_name)
        return ext.replace('.', '')

    def _get_zip_content(self):
        return 'usfm' if self.format == 'zip' else ''

    def to_dict(self):
        return self.__dict__


def generate_json(path_to_results_folder):
    languages = []

    for content_folder in os.listdir(path_to_results_folder):
        path_to_content_folder = os.path.join(path_to_results_folder, content_folder)

        if not os.path.isdir(path_to_content_folder):
            print('%s is not a folder. Skipping...' % path_to_content_folder)
            continue

        language = Language(content_folder)
        content = Content(content_folder)

        for file_name in os.listdir(path_to_content_folder):
            path_to_file = os.path.join(path_to_content_folder, file_name)

            if '.zip' in file_name:
                link = Link(path_to_file)
                content.add_link(link)
            elif '.usfm' in file_name:
                subcontent = Subcontent(file_name)
                link = Link(path_to_file)
                subcontent.add_link(link)
                content.add_subcontent(subcontent)

        language.add_content(content)
        languages.append(language)

    return [language.to_dict() for language in languages]


def write_to_file(data, destination):
    with open(os.path.abspath(destination), 'w') as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    path_to_results_folder = 'results'

    with open('data/books.json', 'r') as f:
        book_data = json.loads(unicode(f.read()))

    data = generate_json(path_to_results_folder)
    write_to_file(data, './data.json')

    print "Done."
