from typing import Dict, List, Tuple


def build_comment_body(
    dead_links: Dict[str, List[Tuple[str, str, str]]],
    checked_files: int,
    checked_links: int,
    method_counts: Dict[str, int],
) -> str:
    lines = []
    lines.append("## Deadlink Sentinel Report")
    lines.append("")
    lines.append(
        f"- Files scanned: {checked_files}, links checked: {checked_links} "
        f"(requests: {method_counts.get('requests', 0)}, browser: {method_counts.get('browser', 0)})"
    )

    if not dead_links:
        lines.append("- ✅ No dead links found.")
        return "\n".join(lines)

    lines.append("")
    lines.append("| File | Dead Link | Method | Error |")
    lines.append("| --- | --- | --- | --- |")
    for file_path, links in dead_links.items():
        for url, method, error in links:
            safe_error = error.replace("\n", " ")
            lines.append(f"| `{file_path}` | {url} | {method} | {safe_error} |")

    return "\n".join(lines)

