Process pending mem-bank jobs.

Without arguments: drains all unprocessed jobs from `small-jobs.json`.
With `--session-id <sid>`: re-processes all jobs for that session (even if already processed).

```bash
python3 plugins/mneme/small-job-worker.py $ARGUMENTS
```
