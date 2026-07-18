#!/usr/bin/env python3

import base64
import importlib.util
from pathlib import Path
import tempfile


SCRIPT = Path(__file__).with_name("generate_video.py")
SPEC = importlib.util.spec_from_file_location("generate_video", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        image = Path(temp_dir) / "frame.png"
        image.write_bytes(b"png")
        request = MODULE.build_vertex_request(
            "assemble",
            "gemini-omni-flash-preview",
            "16:9",
            "5s",
            image_path=[str(image)],
        )
        assert request["generation_config"]["video_config"]["task"] == "reference_to_video"
        assert request["input"][1]["data"] == base64.b64encode(b"png").decode("ascii")
        assert "delivery" not in request["response_format"][0]

        output = Path(temp_dir) / "video.mp4"
        MODULE.save_vertex_video(
            {"steps": [{"content": [{"type": "video", "data": base64.b64encode(b"mp4").decode("ascii")}]}]},
            str(output),
            "unused",
        )
        assert output.read_bytes() == b"mp4"
    print("PASS  Vertex request and response self-check")


if __name__ == "__main__":
    main()
