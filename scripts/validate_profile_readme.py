#!/usr/bin/env python3
"""Validate the profile README's structural redesign constraints."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit


EXPLOSION_GIF = "https://media0.giphy.com/media/A9mRuRtTa6wYHQgVVi/giphy.gif"
PINNED_PROJECT_URLS = {
    "https://github.com/Nothrovo/Solythis-DnD",
    "https://github.com/Nothrovo/Damsel-and-Desire",
    "https://github.com/Nothrovo/Arbiter",
    "https://github.com/Nothrovo/Neuropetra-IP",
    "https://github.com/HETSHI-PLAY/DIPTERA",
}
MEDCHAIN_PROJECT_URL = "https://github.com/Nothrovo/MedChain"
STATS_URL_RE = re.compile(
    r"(?:github-readme-stats|github-readme-streak-stats|streak-stats)", re.IGNORECASE
)
MARKDOWN_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^\s)]+)(?:\s+[^)]*)?\)")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^\s)]+)(?:\s+[^)]*)?\)")
HTML_TAG_RE = re.compile(r"<(?:[^>\"']|\"[^\"]*\"|'[^']*')*>", re.DOTALL)
QUOTED_ATTR_RE = re.compile(r"\b([A-Za-z_:][\w:.-]*)\s*=\s*([\"'])(.*?)\2", re.DOTALL)
URL_RE = re.compile(r"(?:https?://|mailto:)[^\s)>\"']+", re.IGNORECASE)
REFERENCE_USAGE_RE = re.compile(r"!?\[[^\]\n]+\]\s*\[[^\]\n]*\]")
REFERENCE_DEFINITION_RE = re.compile(r"^[ ]{0,3}\[[^\]\n]+\]:\s*\S+", re.MULTILINE)
PIPE_TABLE_RE = re.compile(
    r"^\s*\|?.+\|.+\|?\s*\n\s*\|?\s*:?-{3,}:?\s*\|(?:\s*:?-{3,}:?\s*\|?)+\s*$",
    re.MULTILINE,
)


def _blank(segment: str) -> str:
    """Replace source with whitespace while retaining offsets and line structure."""
    return "".join("\n" if char == "\n" else " " for char in segment)


def mask_hidden_source(text: str) -> str:
    """Mask fenced/inline code and HTML comments without changing offsets."""
    masked = list(text)

    def hide(start: int, end: int) -> None:
        masked[start:end] = _blank(text[start:end])

    # Fences are recognized at line starts and mask through the matching fence.
    fence_re = re.compile(r"(?m)^[ \t]{0,3}(`{3,}|~{3,})[^\n]*(?:\n|$)")
    position = 0
    while True:
        opening = fence_re.search(text, position)
        if not opening:
            break
        marker = opening.group(1)
        closing_re = re.compile(
            rf"(?m)^[ \t]{{0,3}}{re.escape(marker[0])}{{{len(marker)},}}[ \t]*(?:\n|$)"
        )
        closing = closing_re.search(text, opening.end())
        end = closing.end() if closing else len(text)
        hide(opening.start(), end)
        position = end

    # Comments are source-hidden even when they contain Markdown-like constructs.
    for match in re.finditer(r"<!--[\s\S]*?(?:-->|\Z)", text):
        hide(match.start(), match.end())

    interim = "".join(masked)
    # Backtick runs delimit inline code. Unclosed runs mask through end of line.
    inline_re = re.compile(r"(`+)([^\n]*?)(?:\1|(?=\n|\Z))")
    for match in inline_re.finditer(interim):
        hide(match.start(), match.end())
    return "".join(masked)


def html_tags(text: str) -> list[tuple[int, str]]:
    return [(match.start(), match.group(0)) for match in HTML_TAG_RE.finditer(text)]


def quoted_attrs(tag: str) -> dict[str, str]:
    return {match.group(1).lower(): match.group(3) for match in QUOTED_ATTR_RE.finditer(tag)}


def has_unquoted_attr(tag: str, name: str) -> bool:
    assignment = re.search(rf"\b{re.escape(name)}\s*=\s*", tag, re.IGNORECASE)
    if not assignment:
        return False
    rest = tag[assignment.end():].lstrip()
    return not rest.startswith(('"', "'"))


def link_entries(text: str) -> list[tuple[int, str]]:
    """Return supported, active inline Markdown links."""
    markdown_source = strip_html_tags(text)
    return [
        (match.start(), match.group(2))
        for match in MARKDOWN_LINK_RE.finditer(markdown_source)
    ]


def image_entries(text: str) -> list[tuple[int, str, str]]:
    """Return supported, active images as (offset, URL, alt text)."""
    images = [
        (match.start(), match.group(2), match.group(1))
        for match in MARKDOWN_IMAGE_RE.finditer(text)
    ]
    for offset, tag in html_tags(text):
        if re.match(r"<img\b", tag, re.IGNORECASE):
            attrs = quoted_attrs(tag)
            images.append((offset, attrs.get("src", ""), attrs.get("alt", "")))
    return sorted(images)


def first_image_entry(text: str) -> tuple[str, str, str, str] | None:
    """Return the first rendered image as (kind, URL, alt, source tag)."""
    markdown_source = strip_html_tags(text)
    candidates = [
        (match.start(), "markdown", match.group(2), match.group(1), match.group(0))
        for match in MARKDOWN_IMAGE_RE.finditer(markdown_source)
    ]
    for offset, tag in html_tags(text):
        if re.match(r"<img\b", tag, re.IGNORECASE):
            attrs = quoted_attrs(tag)
            candidates.append((offset, "html", attrs.get("src", ""), attrs.get("alt", ""), tag))
    if not candidates:
        return None
    _, kind, url, alt, source = min(candidates, key=lambda candidate: candidate[0])
    return kind, url, alt, source


def strip_html_tags(text: str) -> str:
    return HTML_TAG_RE.sub(lambda match: _blank(match.group(0)), text)


def native_visible_text(active: str) -> str:
    """Keep rendered prose while removing destinations, images, tags, and URLs."""
    text = MARKDOWN_IMAGE_RE.sub(lambda match: _blank(match.group(0)), active)
    text = MARKDOWN_LINK_RE.sub(lambda match: match.group(1) + _blank(match.group(0)[len(match.group(1)) :]), text)
    text = strip_html_tags(text)
    return URL_RE.sub(lambda match: _blank(match.group(0)), text)


def meaningful_alt(alt: str) -> bool:
    words = re.findall(r"[A-Za-z]+", alt)
    if len(words) >= 2:
        return True
    if len(words) != 1:
        return False
    word = words[0]
    return len(word) >= 4 and len(set(word.lower())) > 1


def validate(text: str) -> list[str]:
    failures: list[str] = []
    active = mask_hidden_source(text)
    lowered = active.lower()
    images = image_entries(active)
    links = link_entries(active)
    visible_text = native_visible_text(active)

    if REFERENCE_USAGE_RE.search(active) or REFERENCE_DEFINITION_RE.search(active):
        failures.append("reference-style Markdown links/images are unsupported; use inline syntax")

    tags = html_tags(active)
    if any(re.match(r"</?a(?:\s|>)", tag, re.IGNORECASE) for _, tag in tags):
        failures.append("HTML anchors are unsupported; use inline Markdown links")

    for _, tag in tags:
        if re.match(r"<img\b", tag, re.IGNORECASE):
            for attr in ("src", "alt"):
                if has_unquoted_attr(tag, attr):
                    failures.append(f"HTML img {attr} must use a quoted {attr} attribute")

    first_image = first_image_entry(active)
    if first_image is None or first_image[1] != EXPLOSION_GIF:
        failures.append(f"explosion GIF must be the first image and use exactly {EXPLOSION_GIF}")

    if (
        first_image is None
        or first_image[0] != "html"
        or first_image[1] != EXPLOSION_GIF
        or not meaningful_alt(first_image[2])
        or quoted_attrs(first_image[3]).get("width") != "440"
    ):
        failures.append("first explosion GIF HTML image width must be exactly 440")

    gif_count = sum(bool(re.search(r"\.gif(?:[?#].*)?$", url, re.IGNORECASE)) for _, url, _ in images)
    if gif_count != 1:
        failures.append(f"exactly one GIF is required; found {gif_count}")

    if "streak-stats" in lowered:
        failures.append("streak-stats is forbidden")

    typing_urls = [url for _, url, _ in images if "readme-typing-svg" in url.lower()]
    typing_query: list[tuple[str, str]] = []
    if len(typing_urls) == 1:
        typing_query = parse_qsl(urlsplit(html.unescape(typing_urls[0])).query, keep_blank_values=True)
    fonts = [value for name, value in typing_query if name == "font"]
    lines = [value for name, value in typing_query if name == "lines"]
    if (
        len(typing_urls) != 1
        or fonts != ["Space Mono"]
        or lines != ["Evidence first. Detonate."]
    ):
        failures.append(
            "typing SVG must be exactly one image with font=Space+Mono and exactly "
            "lines=Evidence+first.+Detonate."
        )

    capsule_count = sum("capsule-render" in url.lower() for _, url, _ in images)
    if capsule_count > 2:
        failures.append(f"capsule-render images must be <= 2; found {capsule_count}")

    br_count = len(re.findall(r"<br\b", active, re.IGNORECASE))
    if br_count != 0:
        failures.append(f"manual <br> occurrences must be exactly zero; found {br_count}")

    shield_count = sum("img.shields.io" in url.lower() for _, url, _ in images)
    if shield_count > 18:
        failures.append(f"img.shields.io occurrences must be <= 18; found {shield_count}")

    stats_images = [(offset, url) for offset, url, _ in images if STATS_URL_RE.search(url)]
    if stats_images:
        failures.append(f"stats cards are forbidden; found {len(stats_images)}")

    h1_lines = re.findall(r"^#\s+(.+)$", visible_text, re.MULTILINE)
    if not any("Hadi Nurhasan Darma" in line and "Nothrovo" in line for line in h1_lines):
        failures.append("native Markdown H1 must contain Hadi Nurhasan Darma and Nothrovo")

    for phrase in ("Cyber SOC Analyst", "Web Developer"):
        if phrase not in visible_text:
            failures.append(f"native text must contain {phrase}")

    destinations = {destination for _, destination in links}
    h3_project_urls = re.findall(
        r"^### \[[^]\n]+\]\(([^\s)]+)\)$", active, re.MULTILINE
    )
    if (
        len(h3_project_urls) != 5
        or len(set(h3_project_urls)) != 5
        or set(h3_project_urls) != PINNED_PROJECT_URLS
    ):
        failures.append("Selected Work must contain exactly five unique required Markdown H3 project links")
    if MEDCHAIN_PROJECT_URL in {destination for _, destination in links}:
        failures.append("MedChain project link is forbidden; represent MedChain only through skills")

    if any(not meaningful_alt(alt) for _, _, alt in images):
        failures.append("all images must have meaningful nonempty alt text")

    if any(
        re.match(r"</?(?:style|script)\b", tag, re.IGNORECASE)
        or re.search(r"\bstyle\s*=", tag, re.IGNORECASE)
        for _, tag in tags
    ):
        failures.append("forbidden HTML/CSS found: style/script tags and style= are not allowed")
    if PIPE_TABLE_RE.search(active) or re.search(
        r"</?(?:table|caption|colgroup|col|thead|tbody|tfoot|tr|th|td)\b", active, re.IGNORECASE
    ):
        failures.append("table markup is forbidden")

    if "mailto:hadinurhasandarma@gmail.com" not in destinations:
        failures.append("a mailto email link is required")
    if "https://github.com/Nothrovo" not in destinations:
        failures.append("a GitHub Nothrovo profile link is required")
    if "https://www.linkedin.com/in/hadind" not in destinations:
        failures.append("a LinkedIn /in/hadind link is required")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readme", type=Path, help="path to README.md")
    args = parser.parse_args()

    try:
        text = args.readme.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        parser.error(str(exc))

    failures = validate(text)
    if failures:
        print(f"FAIL: {args.readme}")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"PASS: {args.readme}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
