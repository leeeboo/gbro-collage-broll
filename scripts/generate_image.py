#!/usr/bin/env python3
"""Generate a still image with Gemini 3 Pro Image on Vertex AI."""

import argparse
import os
from pathlib import Path

from google import genai
from google.genai import types


DEFAULT_MODEL = "gemini-3-pro-image"


def generate_image(prompt, output, project, location, model, aspect_ratio):
    if not project:
        raise RuntimeError(
            "Vertex project is missing. Set GOOGLE_CLOUD_PROJECT or OMNI_PROJECT_ID."
        )

    client = genai.Client(vertexai=True, project=project, location=location)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
        ),
    )

    for candidate in response.candidates or []:
        for part in candidate.content.parts or []:
            if part.inline_data and part.inline_data.data:
                output_path = Path(output).expanduser().resolve()
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(part.inline_data.data)
                return output_path

    raise RuntimeError("Vertex returned no image data.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a still image with Gemini 3 Pro Image on Vertex AI."
    )
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--output", required=True, help="Output image path")
    parser.add_argument("--aspect-ratio", default="9:16")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--project",
        default=os.environ.get("OMNI_PROJECT_ID")
        or os.environ.get("GOOGLE_CLOUD_PROJECT"),
    )
    parser.add_argument(
        "--location",
        default=os.environ.get("OMNI_LOCATION")
        or os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
    )
    args = parser.parse_args()

    output = generate_image(
        prompt=args.prompt,
        output=args.output,
        project=args.project,
        location=args.location,
        model=args.model,
        aspect_ratio=args.aspect_ratio,
    )
    print(f"Saved {args.model} image to {output}")


if __name__ == "__main__":
    main()
