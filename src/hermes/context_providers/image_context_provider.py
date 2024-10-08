from argparse import ArgumentParser
from typing import List

from hermes.context_providers.base import ContextProvider
from hermes.prompt_builders.base import PromptBuilder

class ImageContextProvider(ContextProvider):
    def __init__(self):
        self.image_paths: List[str] = []

    def add_argument(self, parser: ArgumentParser):
        parser.add_argument("--image", action="append", help="Path to image file to include in the context")

    def load_context(self, args):
        if args.image:
            self.image_paths = args.image

    def add_to_prompt(self, prompt_builder: PromptBuilder):
        for image_path in self.image_paths:
            prompt_builder.add_image(image_path, name=f"Image: {image_path}")
