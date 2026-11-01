import requests

API = "https://api.github.com"

class GitHubAPIError(Exception):
    """Raised when GitHub returns an error or the request cannot be completed."""

class GitHubClient:
    def __init__(self, token=None, timeout=20):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "OpenSource-Atlas",
        })
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        self.timeout = timeout

    def _get(self, path, params=None):
        url = path if path.startswith("http") else f"{API}{path}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise GitHubAPIError(f"Could not reach GitHub: {exc}") from exc
        if response.status_code == 404:
            raise GitHubAPIError("Repository or resource not found. Check the owner/name and visibility.")
        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
            reset = response.headers.get("X-RateLimit-Reset", "unknown")
            raise GitHubAPIError(f"GitHub API rate limit reached. Reset timestamp: {reset}. Add a token or wait.")
        if not response.ok:
            detail = response.text[:300]
            raise GitHubAPIError(f"GitHub API error {response.status_code}: {detail}")
        try:
            return response.json()
        except ValueError as exc:
            raise GitHubAPIError("GitHub returned an unreadable response.") from exc

    def get_repo(self, full_name):
        return self._get(f"/repos/{full_name}")

    def get_languages(self, full_name):
        return self._get(f"/repos/{full_name}/languages")

    def get_contributors(self, full_name, limit=20):
        return self._get(f"/repos/{full_name}/contributors", {"per_page": min(limit, 100)})

    def get_commits(self, full_name, limit=100):
        return self._get(f"/repos/{full_name}/commits", {"per_page": min(limit, 100)})

    def get_recent_issues(self, full_name, limit=100):
        # GitHub's issues endpoint includes pull requests; the UI labels them separately.
        return self._get(f"/repos/{full_name}/issues", {"state": "all", "per_page": min(limit, 100), "sort": "created", "direction": "desc"})

    def get_file_text(self, full_name, path, ref):
        data = self._get(f"/repos/{full_name}/contents/{path}", {"ref": ref})
        if isinstance(data, list):
            return ""
        import base64
        if data.get("encoding") != "base64":
            return ""
        try:
            return base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
        except Exception:
            return ""
