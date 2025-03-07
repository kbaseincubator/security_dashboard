# Security Dashboard

* At this moment, it is a python script that generates a csv
* For the future, we could make it set up timed runs, and make this a fastapi that serves a dashboard, and also saves
  historical data to mongo
* Currently, you will have to install dependencies and run the main.py script to generate the csv
* At the moment, it scans all kbase repos. We would need to refactor it to scan kbaseapps and jgi-kbase.

## To Do:

- [ ] Update this README.md with info about your repository
- [ ] Modify `Dockerfile` with needed steps (assuming repo produces a Docker image)
- [ ] Ensure
  all [branch rules](https://github.com/kbase/.github/blob/develop/guide/enable-branch-rules.md) & [status checks](https://github.com/kbase/.github/blob/develop/guide/enable-branch-rules.md#require-status-checks)
  are enabled
