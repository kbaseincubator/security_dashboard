import pandas as pd

from src.lib.codecov import get_codecov_coverage_for_all_repos
from src.lib.common import get_all_kbase_repos
from src.lib.constants import REPORTS_DIR, CORE_REPOS
from src.lib.dependabot import get_dependabot_alert_counts_for_repo, get_open_dependabot_prs_for_repo
from src.lib.gha_workflow_tests import get_test_results


def build_report():
    """
    Build a security report of all KBase repositories
    """
    columns = ['repo', 'tests_pass', 'coverage', 'open_dependabot_prs', 'low', 'medium', 'high', 'critical']
    coverage_cache = get_codecov_coverage_for_all_repos()
    report_data = []
    for repo in get_all_kbase_repos():
        repo_name = repo["full_name"]
        default_branch = repo["default_branch"]
        repo_coverage = coverage_cache.get(repo_name.split("/")[-1], {})
        default_coverage = repo_coverage.get(default_branch, {}).get("coverage", "N/A")
        dependabot_cve_counts = get_dependabot_alert_counts_for_repo(repo_name)
        test_workflow_results = get_test_results(repo_full_name=repo_name, default_branch=default_branch)
        pr_count = get_open_dependabot_prs_for_repo(repo_full_name=repo_name)
        report_data.append([repo_name, test_workflow_results, default_coverage, pr_count, *dependabot_cve_counts])

    # Generate CSV
    df = pd.DataFrame(report_data, columns=columns)
    csv_filename = f"{REPORTS_DIR}/github_actions_report.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Report saved to {csv_filename}")
    # Now print  a version of the df to a file with a subset of the data using the list of repos
    csv_filename = f"{REPORTS_DIR}/github_actions_report_subset.csv"
    df[df['repo'].isin(CORE_REPOS)].to_csv(csv_filename, index=False)
    print(f"Subset report saved to {csv_filename}")


build_report()
