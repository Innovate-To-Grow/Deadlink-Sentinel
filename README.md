# Deadlink Sentinel

Deadlink Sentinel is a GitHub Action that scans pull request changes for dead links in Markdown and HTML files. It filters changed files by path and extension before reading them, and validates links with a hybrid strategy: fast HTTP requests first, then a headless Chrome (Selenium) fallback for JavaScript-rendered pages.

## Features
- Filters changed files by include/exclude path prefixes and by file extensions.
- Checks external links; optionally comments on the PR with results.
- Hybrid link validation: `requests` first, Selenium headless Chrome fallback.
- Respects configurable retries, timeouts, and per-file link limits.
- Uses defaults for Markdown/HTML extensions; configurable via inputs.

## Quick Start
```yaml
name: Deadlink Sentinel
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  deadlink:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deadlink Sentinel
        uses: InnovateToGrow/Deadlink-Sentinel@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          include_paths: "docs/,README.md"
          file_extensions: ".md,.mdx"
          fail_on_error: true
```

## Path and Format Filtering
- Scan only docs folder: `include_paths: "docs/"`
- Scan docs + README: `include_paths: "docs/,README.md"`
- Exclude vendor + generated: `exclude_paths: "vendor/,dist/,build/"`
- Scan only Markdown: `file_extensions: ".md,.mdx"`
- Scan only HTML: `file_extensions: ".html,.htm"`
- Combine filters: `include_paths: "docs/"` and `file_extensions: ".md,.mdx"`

Filters are applied to the PR changed file list before any file is read.

## Inputs
| Name | Description | Default |
| --- | --- | --- |
| include_paths | Comma-separated folder/file path prefixes to include (e.g., docs/, README.md). If empty, include all. | `""` |
| exclude_paths | Comma-separated folder/file path prefixes to exclude (e.g., vendor/, node_modules/). | `""` |
| file_extensions | Comma-separated extensions to scan (e.g., .md,.mdx,.html). If empty, use defaults. | `.md,.markdown,.mdx,.html,.htm` |
| fail_on_error | Fail the action if dead links are found. | `true` |
| comment_on_pr | Post a PR comment with dead link findings. | `true` |
| max_retries | Maximum retries for link checks (requests/browser). | `2` |
| timeout_seconds | Timeout in seconds for each link check. | `20` |
| max_links_per_file | Maximum number of links to process per file. | `200` |
| exclude_patterns | Regex pattern(s) to exclude URLs from checking. | `""` |
| include_internal_links | Check internal links in addition to external links. | `false` |

## How It Works
1. Reads inputs and maps them to environment variables.
2. Retrieves the list of PR changed files.
3. Applies filters in order: extension → include_paths → exclude_paths. Only matching files are fetched.
4. Extracts links from Markdown/HTML files up to `max_links_per_file`.
5. Checks each link with `requests` first; if it fails, retries with Selenium headless Chrome for JS-rendered pages.
6. Posts a PR comment when enabled and fails the job when `fail_on_error` is true and dead links remain.

## License
MIT
