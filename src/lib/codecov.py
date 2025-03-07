import json
import logging
import os
from collections import defaultdict

import requests

from src.lib.common import get_all_kbase_repos
from src.lib.constants import TODAY

_coverage_cache = None


def get_codecov_coverage_for_all_repos():
    """Get the coverage for all KBase repositories on 'main', 'master', and 'develop' branches."""
    global _coverage_cache
    if _coverage_cache:
        return _coverage_cache

    ccf = f"cache/coverage_cache_{TODAY}.json"
    if os.path.exists(ccf) and os.path.getsize(ccf) > 0:
        with open(ccf, "r") as f:
            _coverage_cache = json.load(f)
            return _coverage_cache

    coverage = defaultdict(lambda: defaultdict(dict))

    for repo in get_all_kbase_repos():
        owner, repo_name = repo["full_name"].split("/")
        for branch in ["main", "master", "develop"]:
            coverage[repo_name][branch]["coverage"] = get_codecov_coverage(owner, repo_name, branch)

    with open(ccf, "w") as f:
        json.dump(coverage, f, indent=4)
    _coverage_cache = coverage
    return _coverage_cache


def get_codecov_coverage(owner, repo, branch):
    """
    Retrieve coverage from the new Codecov endpoint for a specific branch:
      https://api.codecov.io/api/v2/github/<owner>/repos/<repo>
    Parameters:
      - owner: The GitHub organization or user owning the repository
      - repo: The repository name
      - branch: (Optional) The branch name to filter coverage
    Returns:
      - Coverage percentage (float) or 0 if no coverage data is found
    """

    codecov_url = f"https://api.codecov.io/api/v2/github/{owner}/repos/{repo}/branches/{branch}"
    try:
        resp = requests.get(codecov_url, headers={"accept": "application/json"})
        if resp.status_code == 200:
            data = resp.json()
            totals = data.get("head_commit").get("totals")
            if not totals:
                logging.info(f"No coverage totals available for {owner}/{repo} on branch {branch}.")
                return 0
            coverage = totals.get("coverage", 0) if isinstance(totals, dict) else 0
            return coverage
        else:
            logging.error(f"Error fetching Codecov coverage for {owner}/{repo} on branch {branch}: {resp.status_code}, {resp.text}")
            return 0
    except Exception as e:
        print(f"Exception calling Codecov: {e}")
        return 0
