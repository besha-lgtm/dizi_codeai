import os
from config import ALLOWED_EXTENSIONS, IGNORED_DIRECTORIES


def find_code_files(input_folder):
    code_files = []

    for root, directories, files in os.walk(input_folder):
        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for file_name in files:
            extension = os.path.splitext(file_name)[1].lower()

            if extension in ALLOWED_EXTENSIONS:
                code_files.append(os.path.join(root, file_name))

    return sorted(code_files)
