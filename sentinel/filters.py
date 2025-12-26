import os
from typing import List, Set, Tuple


def normalize_extensions(extensions: List[str]) -> Set[str]:
    normalized: Set[str] = set()
    for ext in extensions:
        clean = ext.strip().lower()
        if not clean:
            continue
        if not clean.startswith("."):
            clean = f".{clean}"
        normalized.add(clean)
    return normalized


def normalize_path_prefixes(paths: List[str]) -> Tuple[Set[str], Set[str]]:
    folder_prefixes: Set[str] = set()
    exact_files: Set[str] = set()
    for raw in paths:
        item = raw.strip().replace("\\", "/")
        if not item:
            continue
        if item.endswith("/"):
            folder_prefixes.add(item)
            continue
        basename = os.path.basename(item)
        if "." in basename:
            exact_files.add(item)
        else:
            folder_prefixes.add(item.rstrip("/") + "/")
    return folder_prefixes, exact_files


def file_matches_filters(
    file_path: str,
    extensions: Set[str],
    include_folders: Set[str],
    include_files: Set[str],
    exclude_folders: Set[str],
    exclude_files: Set[str],
) -> bool:
    normalized_path = file_path.replace("\\", "/")
    lower_path = normalized_path.lower()

    if extensions and not any(lower_path.endswith(ext) for ext in extensions):
        return False

    if include_folders or include_files:
        in_include = normalized_path in include_files or any(
            normalized_path.startswith(prefix) for prefix in include_folders
        )
        if not in_include:
            return False

    if normalized_path in exclude_files or any(
        normalized_path.startswith(prefix) for prefix in exclude_folders
    ):
        return False

    return True

