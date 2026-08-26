"""Small GitHub REST client used by Jibb integrations."""

from __future__ import annotations

import os

import requests
from dotenv import load_dotenv


class GitHubClient:
    def __init__(self, token: str | None = None, timeout: int = 20) -> None:
        load_dotenv()
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout
        self.base_url = "https://api.github.com"

    @property
    def headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "jibb-project-manager",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _get(self, path: str, **params):
        response = requests.get(
            f"{self.base_url}{path}",
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def repository(self, repo: str) -> dict:
        return self._get(f"/repos/{repo}")

    def open_issues(self, repo: str) -> list[dict]:
        items = self._get(f"/repos/{repo}/issues", state="open", per_page=100)
        return [item for item in items if "pull_request" not in item]

    def summary(self, repo: str) -> dict:
        data = self.repository(repo)
        return {
            "full_name": data["full_name"],
            "description": data.get("description"),
            "default_branch": data.get("default_branch"),
            "open_issues": data.get("open_issues_count", 0),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "url": data.get("html_url"),
        }
