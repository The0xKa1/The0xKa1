#!/usr/bin/env python3
"""Restyle the generated cards without changing their text, data, or geometry."""

from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "profile-summary-card-output" / "graywhite"
OUTPUT = SOURCE.with_name("klein")
BLUE = "#002FA7"
NEUTRALS = {"#ffffff": "#ffffff", "#000000": "#161616", "#24292e": "#161616"}
# Use the same color for a language wherever it appears in either chart.
PALETTE = [BLUE, "#161616", "#4B4B4B", "#777777", "#999999", "#BBBBBB", "#DDDDDD",
           "#333333", "#666666", "#AAAAAA"]
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")
CARDS = (
    "0-profile-details.svg",
    "1-repos-per-language.svg",
    "2-most-commit-language.svg",
    "3-stats.svg",
    "4-productive-time.svg",
)


def labels(svg):
    return ["".join(node.itertext()) for node in ET.fromstring(svg).iter()
            if node.tag.endswith("}text")]


def main():
    sources = [(name, (SOURCE / name).read_text()) for name in CARDS]
    colors = dict(NEUTRALS)
    for _, svg in sources:
        for color in HEX.findall(svg):
            key = color.lower()
            if key not in colors:
                index = len(colors) - len(NEUTRALS)
                if index >= len(PALETTE):
                    raise ValueError("The language palette needs another distinct neutral")
                colors[key] = PALETTE[index]

    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, original in sources:
        svg = HEX.sub(lambda match: colors[match[0].lower()], original)
        # Accent the contribution area and hourly bars; leave labels black.
        svg = svg.replace('stroke="#161616" fill="#161616"',
                          f'stroke="{BLUE}" fill="{BLUE}"')
        svg = re.sub(r'(<rect\b[^>]*class="bar"[^>]*fill=")#[0-9A-Fa-f]{6}',
                     lambda match: match[1] + BLUE, svg)
        if labels(svg) != labels(original):
            raise ValueError(f"Card text changed: {name}")
        (OUTPUT / name).write_text(svg + "\n")
    print(f"Styled {len(sources)} cards; all labels and values preserved")


if __name__ == "__main__":
    main()
