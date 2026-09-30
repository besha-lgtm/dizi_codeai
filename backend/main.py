import argparse
import os
from review_service import run_review


def main():
    parser = argparse.ArgumentParser(
        description="AI code review prototype"
    )

    parser.add_argument(
        "repository_url",
        help="Git repository URL to review",
    )

    parser.add_argument(
        "--inventory",
        default="file_inventory.json",
    )

    parser.add_argument(
        "--review",
        default="code_review_result.json",
    )

    args = parser.parse_args()

    result = run_review(
        repository_url=args.repository_url,
        api_key=os.getenv("GEMINI_API_KEY"),
        inventory_path=args.inventory,
        review_path=args.review,
    )

    processed_files = result["processed_files"]

    print("CODE REVIEW COMPLETE")
    print("-" * 40)
    print("Repository URL       :", result["repository_url"])
    print("Files found          :", len(result["code_files"]))
    print("Files processed      :", len(processed_files))
    print("Files sent to Gemini :", len(processed_files))
    print("Review saved         :", args.review)
    print("Inventory saved      :", args.inventory)

    print("\nFiles reviewed:")
    for file_data in processed_files:
        print("-", file_data["file_path"])


if __name__ == "__main__":
    main()
