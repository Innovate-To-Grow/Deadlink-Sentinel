import os
from dataclasses import dataclass
from typing import List

DEFAULT_EXTENSIONS = [".md", ".markdown", ".mdx", ".html", ".htm"]
USER_AGENT = "Deadlink-Sentinel (+https://github.com/InnovateToGrow/Deadlink-Sentinel)"


def parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_csv_list(value: str) -> List[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


@dataclass
class Settings:
    token: str
    fail_on_error: bool
    comment_on_pr: bool
    include_internal_links: bool
    max_retries: int
    timeout_seconds: int
    max_links_per_file: int
    exclude_patterns: str
    include_paths: List[str]
    exclude_paths: List[str]
    file_extensions: List[str]


def load_settings() -> Settings:
    token = os.getenv("GITHUB_TOKEN", "")
    return Settings(
        token=token,
        fail_on_error=parse_bool(os.getenv("FAIL_ON_ERROR"), True),
        comment_on_pr=parse_bool(os.getenv("COMMENT_ON_PR"), True),
        include_internal_links=parse_bool(os.getenv("INCLUDE_INTERNAL_LINKS"), False),
        max_retries=int(os.getenv("MAX_RETRIES", "2")),
        timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "20")),
        max_links_per_file=int(os.getenv("MAX_LINKS_PER_FILE", "200")),
        exclude_patterns=os.getenv("EXCLUDE_PATTERNS", ""),
        include_paths=parse_csv_list(os.getenv("INCLUDE_PATHS", "")),
        exclude_paths=parse_csv_list(os.getenv("EXCLUDE_PATHS", "")),
        file_extensions=parse_csv_list(os.getenv("FILE_EXTENSIONS", "")),
    )

