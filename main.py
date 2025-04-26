from multiprocessing.pool import ThreadPool
from pathlib import Path

import typer
from loguru import logger
from toolz.curried import *
from typing_extensions import Annotated

from libwizard.ai import metadata_generator_pipeline
from libwizard.data import add_book_to_library, generate_book_backup, save_metadata


def main(
    input_path: Annotated[str, typer.Option(prompt="Insert the input path to search for the books", help="Input path to search for the books")],
    output_path: Annotated[str, typer.Option(prompt="Insert the output path to create the library", help="Output path to create the library")],
    prompt_path: Annotated[str, typer.Option(prompt="Please, insert the prompt path", help="Path to look for the prompt")] = ".",
    api_key: str = None,
    n_threads: int = 5,
) -> None:
    input_path, output_path = Path(input_path), Path(output_path)

    validator = compose(list, map(lambda x: x.name))
    files = validator(input_path.glob("*.pdf"))

    logger.info(f"Number of files found: {len(files)}")

    extract_book_metadata = metadata_generator_pipeline(prompt_path, api_key)

    library_generator = compose(generate_book_backup(input_path), add_book_to_library(input_path, output_path), extract_book_metadata)

    with ThreadPool(n_threads) as pool:
        library_metadata = pool.map(library_generator, files)

    _ = save_metadata(output_path, library_metadata)


if __name__ == "__main__":
    typer.run(main)
