import os
import shutil
import subprocess
import tempfile
from urllib.parse import urlparse


def validate_repository_url(repository_url):
    parsed = urlparse(repository_url)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Repository URL must start with http:// or https://")

    if not parsed.netloc:
        raise ValueError("Invalid repository URL.")

    return repository_url.strip()


def clone_repository(repository_url):
    repository_url = validate_repository_url(repository_url)

    repository_name = os.path.splitext(
        os.path.basename(urlparse(repository_url).path.rstrip("/"))
    )[0]

    if not repository_name:
        repository_name = "repository"

    clone_parent = tempfile.mkdtemp(prefix="code_review_")
    repository_path = os.path.join(clone_parent, repository_name)

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repository_url, repository_path],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        shutil.rmtree(clone_parent, ignore_errors=True)
        message = error.stderr.strip() or "Git clone failed."
        raise RuntimeError(message) from error

    return repository_path, clone_parent
