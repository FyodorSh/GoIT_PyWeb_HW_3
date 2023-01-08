import re
import os
import zipfile
import py7zr
import patoolib
import sys
from threading import Thread

import logging

logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = (
    "a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
    "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANS = {}

EXTENSIONS = {('JPEG', 'PNG', 'JPG', 'SVG'): "images",
              ('AVI', 'MP4', 'MOV', 'MKV'): "video",
              ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'): "documents",
              ('MP3', 'OGG', 'WAV', 'AMR', 'M3U',): "audio",
              ('ZIP', 'RAR', '7ZIP', '7Z', 'GZ', 'TAR'): "archives",
              ('JSON', 'CSV',): "dataset",
              ('OTF', 'TTF',): "fonts",
              ('OTF', 'TTF',): "fonts",
              ('FB2', 'EPUB',): "ebooks",
              ('GPX', 'FIT', 'KML'): "gps"}

for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()


class CleanFolder:

    def __init__(self):
        self.sort_dirs = {}
        self.sort_dirs_list = []
        self.dirs_list = []

    @staticmethod
    def translit(input_string: str) -> str:
        return input_string.translate(TRANS)

    @staticmethod
    def normalize(file_name: str):
        regex = r"[^a-zA-Z0-9.]"
        subst = "_"
        file_name = re.sub(regex, subst, CleanFolder().translit(file_name), 0, re.MULTILINE)
        return file_name

    def clean_folders(self, if_empty_delete: bool = False):
        for folder in self.dirs_list:
            self.add_check_task(folder, if_empty_delete)

    def check_dir(self, current_path, if_empty_delete: bool = False):
        # logging.debug(f"Path start - {current_path}")

        if current_path in self.sort_dirs_list:
            return

        for file in os.listdir(current_path):
            file_path = os.path.join(current_path, file)

            if os.path.isdir(file_path):
                if len(os.listdir(file_path)) == 0:
                    if if_empty_delete:
                        os.removedirs(file_path)
                        continue

            file_name_split = os.path.splitext(file)
            file_ext = file_name_split[1].replace(".", "").upper()

            for ext in EXTENSIONS:
                if file_ext in ext:
                    directory = EXTENSIONS.get(ext)
                    sort_dir = self.sort_dirs.get(directory)
                    new_file_name = os.path.join(sort_dir, CleanFolder().normalize(file))
                    os.replace(file_path, new_file_name)
                    if directory == "archives":
                        try:
                            extract_path = os.path.join(sort_dir, CleanFolder.normalize(file_name_split[0]))
                            if file_ext == "7Z":
                                archive = py7zr.SevenZipFile(new_file_name, mode='r')
                                archive.extractall(path=extract_path)
                                archive.close()
                            elif file_ext == "RAR":
                                patoolib.extract_archive(new_file_name, outdir=extract_path, interactive=False)
                            else:
                                with zipfile.ZipFile(new_file_name, 'r') as zip_ref:
                                    zip_ref.extractall(extract_path)
                            os.remove(new_file_name)
                            print(f"{new_file_name} extracted")
                        except:
                            print(f"{file} not zip archive")
                    else:
                        print(f'"{file}" removed and renamed to folder "{directory}"')
        # logging.debug(f"Path end - {current_path}")

    def add_check_task(self, path, if_empty_delete):
        thread = Thread(target=self.check_dir, args=(path, if_empty_delete, ))
        thread.start()

    def get_dirs_list(self, start_path: str):
        self.dirs_list.append(start_path)
        for file in os.listdir(start_path):
            dir_path = os.path.join(start_path, file)
            if os.path.isdir(dir_path):
                if dir_path not in self.sort_dirs_list:
                    self.get_dirs_list(dir_path)

    def create_sort_dir(self, start_path: str):
        for ext in EXTENSIONS:
            sort_dir = EXTENSIONS.get(ext)
            sort_dir_path = os.path.join(start_path, sort_dir)
            if not os.path.exists(sort_dir_path):
                os.mkdir(sort_dir_path)
            self.sort_dirs.update({sort_dir: sort_dir_path})
            self.sort_dirs_list.append(sort_dir_path)

    def clean(self, start_path: str):
        if start_path == '':
            return
        self.create_sort_dir(start_path)
        self.get_dirs_list(start_path)
        self.clean_folders()
        self.clean_folders(True)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Enter path to folder which should be cleaned')
        exit()
    path = sys.argv[1]
    # path = 'e:\\temp\\'
    cleaner = CleanFolder()
    cleaner.clean(path)
    print("Sorting complete.")
