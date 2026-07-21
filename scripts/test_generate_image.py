#!/usr/bin/env python3

import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("generate_image.py")
SPEC = importlib.util.spec_from_file_location("generate_image", SCRIPT)
generate_image = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_image)


class GenerateImageTest(unittest.TestCase):
    def test_saves_inline_image_data(self):
        response = SimpleNamespace(
            candidates=[
                SimpleNamespace(
                    content=SimpleNamespace(
                        parts=[
                            SimpleNamespace(
                                inline_data=SimpleNamespace(data=b"generated-image")
                            )
                        ]
                    )
                )
            ]
        )
        models = SimpleNamespace(generate_content=lambda **kwargs: response)

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "frame.png"
            with patch.object(
                generate_image.genai,
                "Client",
                return_value=SimpleNamespace(models=models),
            ):
                result = generate_image.generate_image(
                    prompt="paper collage",
                    output=output,
                    project="test-project",
                    location="global",
                    model="gemini-3-pro-image",
                    aspect_ratio="16:9",
                )

            self.assertEqual(result, output.resolve())
            self.assertEqual(output.read_bytes(), b"generated-image")


if __name__ == "__main__":
    unittest.main()
