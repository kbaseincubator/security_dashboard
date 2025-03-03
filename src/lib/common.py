import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, Union

import requests

from src.lib.constants import GITHUB_ORG, GITHUB_API_URL, HEADERS, TODAY, CACHE_DIR

logging.basicConfig(level=logging.INFO)


def timed(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record start time
        result = func(*args, **kwargs)  # Call the wrapped function
        end_time = time.time()  # Record end time
        elapsed_time = end_time - start_time  # Calculate elapsed time
        logging.info(f"Function '{func.__name__}' took {elapsed_time:.6f} seconds to complete.")
        return result

    return wrapper


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


@timed
def get_all_kbase_repos():
    """ Check if cache exists with today's date, if not, fetch all KBase repos"""
    # Check if cache exists with today's date
    cache_file = f"{CACHE_DIR}/repos_cache_{TODAY}.json"
    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
        logging.info(f"Using cache file: {cache_file}")
        with open(cache_file, "r") as f:
            return json.load(f)
    # Fetch all KBase repos
    logging.info("Fetching all KBase repos since cache file does not exist")
    repos = _get_repos()
    with open(cache_file, "w") as f:
        # Pretty print the JSON so we can read it
        json.dump(repos, f, indent=4)
    return repos




# TODAY should be defined or imported from somewhere.
# For example, you might define:
# from datetime import date
# TODAY = date.today().isoformat()

def retrieve_cached_data(filetype: str, getter: Callable[[], Any]) -> Union[dict, list]:
    """
    Cache the data fetched by the getter function in a file named
    "cache/{filetype}_cache_{TODAY}.json". If the file already exists and is not empty,
    return the contents of the file. Otherwise, fetch the data using the getter function,
    write it to the file, and return it.

    :param filetype: A string used to differentiate cache file names.
    :param getter: A callable that returns data to be cached.
    :return: The cached data (either a dictionary or a list).
    """
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)  # Ensure the cache directory exists.

    cache_file_path = cache_dir / f"{filetype}_cache_{TODAY}.json"

    # If the cache file exists and is non-empty, load and return its contents.
    if cache_file_path.exists() and cache_file_path.stat().st_size > 0:
        with cache_file_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    # Otherwise, call the getter to fetch data, cache it, and return it.
    data = getter()
    with cache_file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return data
