#!/usr/bin/env python3
"""Validate the generated static site without Node dependencies."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import sys

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.title_parts: list[str] = []
        self.in_title = False
        self.h1_count = 0
        self.meta_description = ""
        self.links: list[str] = []
        self.images: list[tuple[str, str | None]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "html":
            self.lang = data.get("lang") or ""
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta" and data.get("name") == "description":
            self.meta_description = data.get("content") or ""
        if tag == "a" and data.get("href"):
            self.links.append(data["href"] or "")
        if tag == "img":
            self.images.append((data.get("src") or "", data.get("alt")))
        if data.get("id"):
            self.ids.add(data["id"] or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def page_target(href: str, current: Path) -> tuple[Path | None, str]:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc or href.startswith(("mailto:", "tel:", "javascript:")):
        return None, ""
    path = unquote(parsed.path)
    fragment = unquote(parsed.fragment)
    if not path:
        target = current
    elif path.startswith("/"):
        relative = path.lstrip("/")
        target = DIST / relative
    else:
        target = current.parent / path
    if target.is_dir() or path.endswith("/"):
        target = target / "index.html"
    elif target.suffix == "":
        if (target / "index.html").exists():
            target = target / "index.html"
    return target.resolve(), fragment


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text("utf-8"))
    return parser


def main() -> int:
    errors: list[str] = []
    pages = sorted(DIST.rglob("*.html"))
    parsed_pages = {page.resolve(): parse_page(page) for page in pages}

    for page, parser in parsed_pages.items():
        rel = page.relative_to(DIST)
        if parser.lang != "ja":
            errors.append(f"{rel}: html lang is {parser.lang!r}, expected 'ja'")
        if not "".join(parser.title_parts).strip():
            errors.append(f"{rel}: missing title")
        if rel.name != "404.html" and not parser.meta_description.strip():
            errors.append(f"{rel}: missing meta description")
        if parser.h1_count != 1:
            errors.append(f"{rel}: expected exactly one h1, found {parser.h1_count}")
        for src, alt in parser.images:
            if not src:
                errors.append(f"{rel}: image without src")
                continue
            if alt is None:
                errors.append(f"{rel}: image {src} is missing alt attribute")
            parsed = urlparse(src)
            if not parsed.scheme and src.startswith("/"):
                image = DIST / unquote(parsed.path).lstrip("/")
                if not image.exists():
                    errors.append(f"{rel}: missing image {src}")
        for href in parser.links:
            target, fragment = page_target(href, page)
            if target is None:
                continue
            try:
                target.relative_to(DIST.resolve())
            except ValueError:
                errors.append(f"{rel}: link escapes dist: {href}")
                continue
            if not target.exists():
                errors.append(f"{rel}: broken internal link {href} -> {target.relative_to(DIST)}")
                continue
            if fragment and target.suffix == ".html":
                target_parser = parsed_pages.get(target)
                if target_parser is None:
                    target_parser = parse_page(target)
                if fragment not in target_parser.ids:
                    errors.append(f"{rel}: missing fragment #{fragment} in {target.relative_to(DIST)}")

    required = ["assets/site.css", "assets/site.js", "sitemap.xml", "robots.txt", "site.webmanifest", "favicon.svg", "_headers"]
    for name in required:
        if not (DIST / name).exists():
            errors.append(f"missing required output: {name}")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(" -", error)
        return 1
    print(f"Validation passed: {len(pages)} HTML files, no broken internal links or image paths.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
