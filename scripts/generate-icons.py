#!/usr/bin/env python3
"""Генерация favicon / PNG / ICO из пиксельной сетки 16×16 (без внешних зависимостей)."""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

# Знак бесконечности (∞), 16×16. '#' — пиксель переднего плана.
GRID = [
    "................",
    "................",
    "..####....####..",
    ".##..##..##..##.",
    "##....####....##",
    "##.....##.....##",
    ".##...####...##.",
    "..##.##..##.##..",
    "...###....###...",
    "...###....###...",
    "..##.##..##.##..",
    ".##...####...##.",
    "##.....##.....##",
    "##....####....##",
    ".##..##..##..##.",
    "..####....####..",
]

FG = (212, 212, 216, 255)
BG_DARK = (19, 20, 24, 255)


def grid_rgba(bg: tuple[int, int, int, int]) -> bytes:
    w, h = len(GRID[0]), len(GRID)
    out = bytearray(w * h * 4)
    i = 0
    for row in GRID:
        for c in row:
            px = FG if c == "#" else bg
            out[i : i + 4] = px
            i += 4
    return bytes(out)


def upscale_nearest(rgba: bytes, src_w: int, src_h: int, dst_w: int, dst_h: int) -> bytes:
    out = bytearray(dst_w * dst_h * 4)
    for dy in range(dst_h):
        sy = dy * src_h // dst_h
        for dx in range(dst_w):
            sx = dx * src_w // dst_w
            si = (sy * src_w + sx) * 4
            di = (dy * dst_w + dx) * 4
            out[di : di + 4] = rgba[si : si + 4]
    return bytes(out)


def write_png(path: Path, width: int, height: int, rgba: bytes) -> None:
    assert len(rgba) == width * height * 4

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)

    raw = bytearray()
    for y in range(height):
        raw.append(0)
        row_start = y * width * 4
        raw.extend(rgba[row_start : row_start + width * 4])

    compressed = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def write_ico_png_embedded(path: Path, images: list[tuple[int, int, bytes]]) -> None:
    """ICO: список (ширина, высота, тело PNG)."""
    n = len(images)
    header = struct.pack("<HHH", 0, 1, n)
    offset = 6 + n * 16
    entries = bytearray()
    blobs = bytearray()
    for w, h, png_data in images:
        bw = w if w < 256 else 0
        bh = h if h < 256 else 0
        entries.extend(
            struct.pack(
                "<BBBBHHII",
                bw,
                bh,
                0,
                0,
                1,
                32,
                len(png_data),
                offset + len(blobs),
            )
        )
        blobs.extend(png_data)
    path.write_bytes(header + bytes(entries) + bytes(blobs))


def png_bytes(width: int, height: int, rgba: bytes) -> bytes:
    """Возвращает PNG как bytes (для ICO)."""

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)

    raw = bytearray()
    for y in range(height):
        raw.append(0)
        row_start = y * width * 4
        raw.extend(rgba[row_start : row_start + width * 4])
    compressed = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )


def write_svg(path: Path, bg_hex: str, fg_hex: str) -> None:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" role="img">',
        f'  <title>infinity</title>',
        f'  <rect width="16" height="16" fill="{bg_hex}"/>',
        f'  <g fill="{fg_hex}">',
    ]
    for y, row in enumerate(GRID):
        for x, c in enumerate(row):
            if c == "#":
                lines.append(f'    <rect x="{x}" y="{y}" width="1" height="1"/>')
    lines.extend(["  </g>", "</svg>", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_svg_mask(path: Path) -> None:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">',
        '  <g fill="#000000">',
    ]
    for y, row in enumerate(GRID):
        for x, c in enumerate(row):
            if c == "#":
                lines.append(f'    <rect x="{x}" y="{y}" width="1" height="1"/>')
    lines.extend(["  </g>", "</svg>", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    icons = root / "assets" / "icons"
    icons.mkdir(parents=True, exist_ok=True)

    write_svg(icons / "favicon.svg", "#131418", "#d4d4d8")
    write_svg_mask(icons / "safari-pinned-tab.svg")

    base16 = grid_rgba(BG_DARK)
    write_png(icons / "favicon-16x16.png", 16, 16, base16)
    write_png(
        icons / "favicon-32x32.png",
        32,
        32,
        upscale_nearest(base16, 16, 16, 32, 32),
    )
    write_png(
        icons / "apple-touch-icon.png",
        180,
        180,
        upscale_nearest(base16, 16, 16, 180, 180),
    )

    im32 = upscale_nearest(base16, 16, 16, 32, 32)
    im48 = upscale_nearest(base16, 16, 16, 48, 48)
    write_ico_png_embedded(
        icons / "favicon.ico",
        [
            (16, 16, png_bytes(16, 16, base16)),
            (32, 32, png_bytes(32, 32, im32)),
            (48, 48, png_bytes(48, 48, im48)),
        ],
    )

    print("OK:", icons)


if __name__ == "__main__":
    main()
