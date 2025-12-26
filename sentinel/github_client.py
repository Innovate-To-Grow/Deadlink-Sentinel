import json
import os
import sys
from typing import Dict, List, Tuple

from github import Github
from github.PullRequest import PullRequest
from github.Repository import Repository


def load_event_payload() -> Dict:
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        print("[error] GITHUB_EVENT_PATH is missing or invalid.")
        sys.exit(1)
    with open(event_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_repository_and_pr(token: str) -> Tuple[Repository, PullRequest]:
    payload = load_event_payload()
    repo_name = os.getenv("GITHUB_REPOSITORY")
    if not repo_name:
        print("[error] GITHUB_REPOSITORY is not set.")
        sys.exit(1)
    pr_number = payload.get("pull_request", {}).get("number")
    if not pr_number:
        print("[error] This action only runs on pull_request events.")
        sys.exit(1)
    gh = Github(token)
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    return repo, pr


def gather_changed_files(pr: PullRequest) -> List[str]:
    files = []
    for file in pr.get_files():
        if file.status == "removed":
            continue
        files.append(file.filename.replace("\\", "/"))
    return files

