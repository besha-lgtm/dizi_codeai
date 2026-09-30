import os


def read_code_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except UnicodeDecodeError:
        print(f"Could not decode: {file_path}")
        return ""
    except OSError as error:
        print(f"Error reading {file_path}: {error}")
        return ""


def process_code_file(file_path, input_folder):
    code = read_code_file(file_path)
    lines = code.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]

    relative_path = os.path.relpath(file_path, input_folder)

    return {
        "file_name": os.path.basename(file_path),
        "file_path": relative_path,
        "extension": os.path.splitext(file_path)[1].lower(),
        "total_lines": len(lines),
        "code_lines": len(non_empty_lines),
        "characters": len(code),
        "content": code,
    }
