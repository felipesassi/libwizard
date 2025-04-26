import json
from pathlib import Path
import shutil
import time

from loguru import logger
from toolz.curried import *


def create_book_title(output_path: Path, title: str) -> Path:
    output_file_path = output_path / f"{title}.pdf"

    c = 0

    while output_file_path.exists():
        output_file_path = output_path / f"{title} - Duplicated={c}.pdf"

        c = c + 1

    return output_file_path


@curry
def add_book_to_library(input_path: Path, output_path: Path, book: dict[str, str]) -> dict[str, str]:
    input_file_path = input_path / book.get("original_title")

    category = book.get("category", "Without category")
    sub_category = book.get("sub-category", "Without sub-category")

    (output_path / "Books" / category / sub_category).mkdir(parents=True, exist_ok=True)
    
    original_title = book.get("original_title")
    title = book.get("title", original_title).replace("/", "-").replace(":", " -")

    base_output_file_path = output_path / "Books" / category / sub_category
    output_file_path = create_book_title(base_output_file_path, title)

    logger.info(f"Saving data - Input file: {input_file_path.name} | Output file: {output_file_path.name}")

    shutil.copy2(str(input_file_path), str(output_file_path))

    return book


@curry
def generate_book_backup(input_path: Path, book: dict[str, str]) -> dict[str, str]:
    input_file_path = input_path / book.get("original_title")

    output_path = input_path / "PDFs"
    output_path.mkdir(parents=True, exist_ok=True)

    output_file_path = output_path / book.get("original_title")

    logger.info(f"Generating backup - Input file: {input_file_path.name} | Output file: {output_file_path.name}")

    shutil.copy2(str(input_file_path), str(output_file_path))

    return book


def save_metadata(output_path: Path, metadata: list[dict[str, str]]) -> None:
    (output_path / "Books" / "Metadata").mkdir(exist_ok=True)

    with open(output_path / "Books" / "Metadata" / f"{int(time.time())}.json", "w") as f:
        json.dump(metadata, f)
