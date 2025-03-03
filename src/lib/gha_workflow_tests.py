from src.lib.gha_workflows import get_last_n_workflow_runs


def get_test_results(repo_full_name, default_branch="main"):
    last_n_actions = get_last_n_workflow_runs(1)
    last_actions = last_n_actions.get(repo_full_name, {})


    tests = {}

    for action_path in last_actions:
        action = last_actions[action_path].get(default_branch, [])
        last_run = action[0] if action else {}
        conclusion = last_run.get("conclusion", "N/A")
        if conclusion == "success":
            tests[action_path] = True
        elif conclusion == "failure":
            tests[action_path] = False
        else:
            tests[action_path] = "N/A"

    if repo_full_name == "kbase/execution_engine2":
        print(tests)

    for item in tests.values():
        if item is not True:
            return False
    return True
