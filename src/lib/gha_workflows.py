import json
import logging
import os
from collections import defaultdict

import requests

from src.lib.common import get_all_kbase_repos
from src.lib.constants import GITHUB_API_URL, HEADERS, TODAY


def _get_github_actions(repo_full_name):
    """Fetch the GitHub Actions workflows for a given repository."""
    url = f"{GITHUB_API_URL}/repos/{repo_full_name}/actions/workflows"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print(f"Error fetching workflows for {repo_full_name}: {resp.status_code}, {resp.text}")
        return []
    return resp.json().get("workflows", [])


def _get_workflow_runs(repo, workflow_id, branch=None, last_n=5):
    """Fetch the last 'n' runs of a given workflow in a repository, optionally filtering by branch."""
    url = f"{GITHUB_API_URL}/repos/{repo}/actions/workflows/{workflow_id}/runs"
    params = {"per_page": last_n}
    if branch:
        params["branch"] = branch
    resp = requests.get(url, headers=HEADERS, params=params)
    if resp.status_code != 200:
        print(f"Error fetching runs for workflow {workflow_id} in {repo}: {resp.status_code}, {resp.text}")
        return []
    return resp.json().get("workflow_runs", [])



def get_last_n_workflow_runs(last_n=5):
    """
    Get the last 'n' runs for all workflows containing 'test' in the name,
    filtering by branch for 'main', 'master', and 'develop'.
    """

    ignored_workflows = ['.github/workflows/pr_build.yml', '.github/workflows/manual-build.yml',
                         '.github/workflows/release-main.yml', '.github/workflows/release.yml',
                         '.github/workflows/build_test_pr.yaml', '.github/workflows/build_prodrc_pr.yaml',
                         '.github/workflows/tag_latest_image.yaml']


    actions = get_cached_actions_for_all_repos(get_all_kbase_repos())

    cache_file = f"cache/actions_last_{last_n}_cache_{TODAY}.json"
    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
        with open(cache_file, "r") as f:
            return json.load(f)

    last_n_runs = defaultdict(dict)

    for repo, workflows in actions.items():

        for workflow in workflows:

            if workflow['path'] in ignored_workflows or "test" not in workflow['name'].lower():
                continue

            repo_results = {
                "develop": _get_workflow_runs(repo, workflow['id'], branch="develop", last_n=last_n),
                "main": _get_workflow_runs(repo, workflow['id'], branch="main", last_n=last_n),
                "master": _get_workflow_runs(repo, workflow['id'], branch="master", last_n=last_n)
            }
            last_n_runs[repo][workflow['path']] = repo_results
        # Add empty results for repos that don't have any workflows
        if repo not in last_n_runs:
            last_n_runs[repo] = {}

    with open(cache_file, "w") as f:
        json.dump(last_n_runs, f, indent=4)

    return last_n_runs




def get_cached_actions_for_all_repos(repos):
    """Fetch the GitHub Actions workflows for a given repository."""
    cache_file = f"cache/actions_cache_{TODAY}.json"
    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
        with open(cache_file, "r") as f:
            return json.load(f)
    else:
        logging.info("Fetching all githb actions workflow runs since cache file does not exist")
        actions = {}
        for repo in repos:
            repo_full_name = repo['full_name']
            actions[repo_full_name] = _get_github_actions(repo_full_name)
        with open(cache_file, "w") as f:
            # Pretty print the JSON so we can read it
            json.dump(actions, f, indent=4)
        return actions
