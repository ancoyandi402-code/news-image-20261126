#!/usr/bin/env python3
"""Placid Sonar -- News Image 26 November 2026 entrypoint.

Standard library only. The approved front page is shipped in this
repository as entry.png (1024x1024, rendered by the agent in the build
session). This program copies it to the grader's output directory and
validates the copy: the SHA-256 of the copy must match the source, and
the PNG IHDR must say 1024x1024.

The grader runs entries in a fresh container with nothing installed
(RULES.txt: "standard library only: nothing is installed before it
runs"), so this program imports nothing beyond the standard library.
"""

import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_NAME = "entry.png"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path):
    with open(path, "rb") as handle:
        header = handle.read(33)
    if len(header) < 33 or header[:8] != PNG_SIGNATURE:
        raise ValueError("not a PNG file: bad signature in %s" % path)
    chunk_length, chunk_type = struct.unpack(">I4s", header[8:16])
    if chunk_type != b"IHDR" or chunk_length != 13:
        raise ValueError("not a PNG file: first chunk is not IHDR in %s" % path)
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def main():
    source = os.path.join(HERE, SOURCE_NAME)
    if not os.path.isfile(source):
        print("error: %s not found next to main.py" % SOURCE_NAME, file=sys.stderr)
        return 1
    width, height = png_dimensions(source)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        print(
            "error: %s is %dx%d, expected %dx%d"
            % (SOURCE_NAME, width, height, EXPECTED_WIDTH, EXPECTED_HEIGHT),
            file=sys.stderr,
        )
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    destination = os.path.join(out_dir, SOURCE_NAME)
    shutil.copyfile(source, destination)
    source_hash = sha256_of(source)
    dest_hash = sha256_of(destination)
    if source_hash != dest_hash:
        print(
            "error: copy mismatch: source %s != dest %s" % (source_hash, dest_hash),
            file=sys.stderr,
        )
        return 1
    source_size = os.path.getsize(source)
    dest_size = os.path.getsize(destination)
    if source_size != dest_size:
        print(
            "error: size mismatch: source %d bytes != dest %d bytes"
            % (source_size, dest_size),
            file=sys.stderr,
        )
        return 1
    print("wrote %s (%d, %d, %d bytes)" % (destination, width, height, dest_size))
    print("sha256 %s" % dest_hash)
    return 0


if __name__ == "__main__":
    sys.exit(main())
