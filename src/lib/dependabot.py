# Author: bio-boris for the seucrity whitepaper dashboard
import logging
from collections import Counter

import requests

from src.lib.common import timed, get_all_kbase_repos, retrieve_cached_data
from src.lib.constants import GITHUB_API_URL, HEADERS

logger = logging.getLogger(__name__)


def fetch_json(url: str, params: dict | None = None) -> dict | list:
    """
    Perform a GET request to the specified URL with optional query parameters.
    Returns the parsed JSON response if the status code is 200,
    otherwise logs an error and returns an empty list.
    """
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    logger.error("Error fetching %s: %s, %s", url, response.status_code, response.text)
    return []


def get_dependabot_alerts(repo_full_name: str) -> dict | list:
    """
    Fetch Dependabot alerts for the given repository.
    """
    url = f"{GITHUB_API_URL}/repos/{repo_full_name}/dependabot/alerts"
    logger.debug("Fetching alerts from URL: %s", url)
    return fetch_json(url)


def get_open_dependabot_prs(repo_full_name: str) -> dict | list:
    """
    Fetch open Dependabot pull requests for the given repository.
    """
    url = f"{GITHUB_API_URL}/repos/{repo_full_name}/pulls"
    params = {"state": "open", "creator": "dependabot[bot]"}
    return fetch_json(url, params=params)


@timed
def get_dependabot_security_alerts_for_all_repos() -> dict:
    """
    Fetch Dependabot alerts for all KBase repositories using caching.
    Retrieves alerts for each repository and caches the result to avoid redundant API calls.
    """

    def get_alerts() -> dict:
        # Build a dictionary mapping each repository's full name to its alerts.
        return {repo["full_name"]: get_dependabot_alerts(repo["full_name"]) for repo in get_all_kbase_repos()}

    return retrieve_cached_data("dependabot_alerts", get_alerts)


@timed
def get_open_dependabot_prs_for_all_repos() -> dict:
    """
    Fetch open Dependabot pull requests for all KBase repositories using caching.
    Retrieves open PRs for each repository and caches the result to avoid redundant API calls.
    """

    def get_prs() -> dict:
        # Build a dictionary mapping each repository's full name to its open Dependabot PRs.
        return {repo["full_name"]: get_open_dependabot_prs(repo["full_name"]) for repo in get_all_kbase_repos()}

    return retrieve_cached_data("dependabot_prs", get_prs)


def get_open_dependabot_prs_for_repo(repo_full_name: str ) -> int:
    """
    Return the number of open Dependabot pull requests for the specified repository.
    Uses cached data if available, otherwise fetches the data.
    """
    data = get_open_dependabot_prs_for_all_repos()
    return len(data.get(repo_full_name, []))


def get_dependabot_alert_counts_for_repo(repo_full_name: str) -> list:
    """
    Return a breakdown of Dependabot alert counts by severity for the specified repository.
    If no alerts are found, returns ["N/A", "N/A", "N/A", "N/A"].
    """
    data = get_dependabot_security_alerts_for_all_repos()

    cves = data.get(repo_full_name, [])
    if not cves:
        return ["N/A"] * 4
    # Count alerts by severity.
    c = Counter(item["security_advisory"]["severity"] for item in cves)
    return [c.get('low', 0), c.get('medium', 0), c.get('high', 0), c.get('critical', 0)]
