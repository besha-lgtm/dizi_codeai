import os
import shutil
from code_scanner import find_code_files
from file_processor import process_code_file
from code_inventory import create_inventory, save_inventory
from gemini_reviewer import review_all_files, save_review_result
from repository_cloner import clone_repository


def process_project(repository_path: str):
    code_files = find_code_files(repository_path)
    processed_files = []

    for file_path in code_files:
        file_data = process_code_file(file_path, repository_path)
        if file_data["content"].strip():          # skip empty files
            processed_files.append(file_data)

    return code_files, processed_files


def run_review(
    repository_url: str,
    api_key: str | None = None,
    audit_type: str = "everything",
    inventory_path: str = "file_inventory.json",
    review_path: str = "code_review_result.json",
) -> dict:
    """
    Full pipeline:
      1. Clone repo
      2. Scan & process code files
      3. Send to Gemini with audit_type context
      4. Return structured result dict
    """
    repository_path, clone_parent = clone_repository(repository_url)

    try:
        code_files, processed_files = process_project(repository_path)

        if not processed_files:
            raise ValueError("No supported code files found in the repository.")

        # Save inventory (optional)
        inventory = create_inventory(processed_files)
        save_inventory(inventory, inventory_path)

        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY was not provided.")

        # Run LLM review — returns structured dict
        review_data = review_all_files(processed_files, api_key, audit_type)

        # Attach metadata
        review_data["repository_url"] = repository_url
        review_data["audit_type"] = audit_type
        review_data["files_found"] = len(code_files)
        review_data["files_processed"] = len(processed_files)

        # Save to disk (optional)
        save_review_result(review_data, review_path)

        return {
            "repository_url": repository_url,
            "repository_path": repository_path,
            "code_files": code_files,
            "processed_files": processed_files,
            "inventory": inventory,
            "review_result": review_data,
        }

    finally:
        shutil.rmtree(clone_parent, ignore_errors=True)
