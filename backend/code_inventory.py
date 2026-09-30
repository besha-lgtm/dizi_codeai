import json


def create_inventory(processed_files):
    return [
        {
            "file_name": file_data["file_name"],
            "file_path": file_data["file_path"],
            "extension": file_data["extension"],
            "total_lines": file_data["total_lines"],
            "code_lines": file_data["code_lines"],
            "characters": file_data["characters"],
        }
        for file_data in processed_files
    ]


def save_inventory(inventory, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(inventory, file, indent=4, ensure_ascii=False)
