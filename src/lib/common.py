import json
import logging
import os
import sys

import requests

from src.lib.constants import GITHUB_ORG, GITHUB_API_URL, HEADERS, TODAY, CACHE_DIR

logging.basicConfig(level=logging.INFO)


def _get_repos():
    """Fetch all repositories in the given GitHub organization."""
    url = f"{GITHUB_API_URL}/orgs/{GITHUB_ORG}/repos"
    repos = []
    page = 1
    while True:
        resp = requests.get(url, headers=HEADERS, params={"page": page, "per_page": 100})
        if resp.status_code != 200:
            print(f"Error fetching repos: {resp.status_code}, {resp.text}")
            sys.exit(1)

        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos


_kbase_repos_cache = None


def get_all_kbase_repos():
    """ Check if cache exists with today's date, if not, fetch all KBase repos"""
    # Check if cache exists with today's date
    cache_file = f"{CACHE_DIR}/repos_cache_{TODAY}.json"
    global _kbase_repos_cache
    if _kbase_repos_cache:
        return _kbase_repos_cache

    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
        with open(cache_file, "r") as f:
            _kbase_repos_cache = json.load(f)
            return _kbase_repos_cache

    logging.info("Fetching all KBase repos since cache file does not exist")
    repos = _get_repos()
    with open(cache_file, "w") as f:
        json.dump(repos, f, indent=4)
    _kbase_repos_cache = repos
    return _kbase_repos_cache
