import re
from typing import List, Pattern, Set


def extract_links(
    file_content: str,
    file_extension: str,
    max_links: int,
    exclude_regex: Pattern | None,
) -> List[str]:
    links: List[str] = []
    seen: Set[str] = set()

    def add_link(url: str) -> None:
        if not url.lower().startswith(("http://", "https://")):
            return
        if exclude_regex and exclude_regex.search(url):
            return
        if url in seen:
            return
        seen.add(url)
        links.append(url)

    md_link = re.compile(r"\[[^\]]+\]\((https?://[^\s)]+)\)")
    md_autolink = re.compile(r"<(https?://[^>\s]+)>")
    html_link = re.compile(r'(?:href|src)\s*=\s*["\'](https?://[^"\']+)["\']', re.IGNORECASE)

    ext = file_extension.lower()
    if ext in {".md", ".markdown", ".mdx"}:
        for match in md_link.findall(file_content):
            add_link(match)
            if len(links) >= max_links:
                return links
        for match in md_autolink.findall(file_content):
            add_link(match)
            if len(links) >= max_links:
                return links
    elif ext in {".html", ".htm"}:
        for match in html_link.findall(file_content):
            add_link(match)
            if len(links) >= max_links:
                return links

    return links[:max_links]

