import os
from typing import Callable

from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from loguru import logger
from toolz.curried import *

load_dotenv()


Pipeline = Callable[[str], dict[str, str]]


def metadata_generator_pipeline(prompt_path: str, api_key: str) -> Pipeline:
    api_key = os.getenv("API_KEY") if api_key is None else api_key
    prompt_path = "prompt.txt" if prompt_path == "." else prompt_path

    with open(prompt_path, "r") as file:
        template = file.read()

    prompt = PromptTemplate(template=template, input_variables=["name"])
    model = OpenAI(model_name="gpt-3.5-turbo-instruct", temperature=0.0, api_key=api_key, max_retries=5)
    parser = JsonOutputParser()

    pipeline = prompt | model | parser

    def f(book: str) -> dict[str, str]:
        try:
            metadata = pipeline.invoke({"name": book}) | {"original_title": book}

            return {k.lower(): v for k, v in metadata.items()}

        except Exception as e:
            logger.error(f"Error during analysis of: {book} | {e}")

            return {"original_title": book}

    return f
