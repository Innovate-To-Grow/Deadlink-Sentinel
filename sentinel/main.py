import os
import re
import sys
from typing import Dict, List, Tuple

from sentinel.checker import check_link_hybrid, init_selenium_driver
from sentinel.config import DEFAULT_EXTENSIONS, Settings, load_settings
from sentinel.filters import (
    file_matches_filters,
    normalize_extensions,
    normalize_path_prefixes,
)
from sentinel.github_client import gather_changed_files, get_repository_and_pr
from sentinel.links import extract_links
from sentinel.report import build_comment_body


def _compile_filters(settings: Settings) -> Tuple[Dict[str, List[str]], re.Pattern | None]:
    extensions = normalize_extensions(
        settings.file_extensions if settings.file_extensions else DEFAULT_EXTENSIONS
    )
    include_folders, include_files = normalize_path_prefixes(settings.include_paths)
    exclude_folders, exclude_files = normalize_path_prefixes(settings.exclude_paths)
    exclude_regex = re.compile(settings.exclude_patterns) if settings.exclude_patterns else None
    filter_sets = {
        "extensions": extensions,
        "include_folders": include_folders,
        "include_files": include_files,
        "exclude_folders": exclude_folders,
        "exclude_files": exclude_files,
    }
    return filter_sets, exclude_regex


def _filter_changed_files(changed_files: List[str], filter_sets: Dict[str, List[str]]) -> List[str]:
    return [
        path
        for path in changed_files
        if file_matches_filters(
            path,
            filter_sets["extensions"],
            filter_sets["include_folders"],
            filter_sets["include_files"],
            filter_sets["exclude_folders"],
            filter_sets["exclude_files"],
        )
    ]


def _process_files(
    repo,
    pr,
    filtered_files: List[str],
    include_internal_links: bool,
    max_links_per_file: int,
    exclude_regex: re.Pattern | None,
    timeout_seconds: int,
    max_retries: int,
):
    driver = init_selenium_driver(timeout_seconds)
    dead_links: Dict[str, List[Tuple[str, str, str]]] = {}
    method_counts: Dict[str, int] = {"requests": 0, "browser": 0}
    total_links_checked = 0

    for file_path in filtered_files:
        try:
            content_file = repo.get_contents(file_path, ref=pr.head.sha)
            content = content_file.decoded_content.decode("utf-8", errors="ignore")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[warn] Unable to fetch file {file_path}: {exc}")
            continue

        ext = os.path.splitext(file_path)[1].lower()
        links = extract_links(content, ext, max_links_per_file, exclude_regex)

        if not links:
            continue

        for url in links:
            if not include_internal_links and not url.lower().startswith(("http://", "https://")):
                continue

            alive, method, error = check_link_hybrid(
                url, driver, timeout_seconds, max_retries
            )
            method_counts[method] = method_counts.get(method, 0) + 1
            total_links_checked += 1

            if not alive:
                dead_links.setdefault(file_path, []).append((url, method, error))

    if driver:
        try:
            driver.quit()
        except Exception:  # pylint: disable=broad-except
            pass

    return dead_links, method_counts, total_links_checked


def main() -> None:
    settings = load_settings()
    if not settings.token:
        print("[error] GITHUB_TOKEN is required.")
        sys.exit(1)

    filter_sets, exclude_regex = _compile_filters(settings)
    repo, pr = get_repository_and_pr(settings.token)
    changed_files = gather_changed_files(pr)

    filtered_files = _filter_changed_files(changed_files, filter_sets)
    if not filtered_files:
        print("[info] No changed files matched the filters. Exiting.")
        sys.exit(0)

    dead_links, method_counts, total_links_checked = _process_files(
        repo,
        pr,
        filtered_files,
        settings.include_internal_links,
        settings.max_links_per_file,
        exclude_regex,
        settings.timeout_seconds,
        settings.max_retries,
    )

    checked_files_count = len(filtered_files)
    comment_body = build_comment_body(dead_links, checked_files_count, total_links_checked, method_counts)

    if settings.comment_on_pr:
        try:
            pr.create_issue_comment(comment_body)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[warn] Failed to post PR comment: {exc}")

    if dead_links:
        print("[error] Dead links detected:")
        for file_path, links in dead_links.items():
            for url, method, error in links:
                print(f" - {file_path}: {url} (via {method}) -> {error}")
        if settings.fail_on_error:
            sys.exit(1)

    print("[info] Completed link checks. No blocking issues.")
    sys.exit(0)

