# Prefect Cloud dashboard (adjust account/workspace in URL as needed):
# https://app.prefect.cloud/
#
# API reference: https://app.prefect.cloud/api/docs
#
# Usage:
#   export PREFECT_API_KEY="pnu_..."   # required — never commit real keys
#   python Prefect/api/deploymentAPI.py

import json
import os
import sys

import requests

ACCOUNT_ID = "37604d35-88fc-4011-9763-0d9cf1b6871f"
WORKSPACE_ID = "92d71a09-2bc6-4a9a-b524-98216df7b1e4"
DEPLOYMENT_ID = "fc2e7a01-88aa-460f-97c2-8d447652cc40"

PREFECT_API_URL = (
    f"https://api.prefect.cloud/api/accounts/{ACCOUNT_ID}"
    f"/workspaces/{WORKSPACE_ID}/deployments/{DEPLOYMENT_ID}"
)


def _print_deployment_summary(d: dict) -> None:
    """Print rubric-friendly fields for documentation screenshots."""
    sched = d.get("schedule") or {}
    interval_sec = sched.get("interval")
    version_info = d.get("version_info") or {}

    print("\n--- Deployment summary (for report) ---")
    print(f"  name:                 {d.get('name')}")
    print(f"  id:                   {d.get('id')}")
    print(f"  flow_id:              {d.get('flow_id')}")
    print(f"  entrypoint:           {d.get('entrypoint')}")
    print(f"  schedule interval:    {interval_sec} s  ({(interval_sec or 0) / 60:.0f} min)")
    print(f"  schedule timezone:    {sched.get('timezone')}")
    print(f"  is_schedule_active:   {d.get('is_schedule_active')}")
    print(f"  paused:               {d.get('paused')}")
    print(f"  status:               {d.get('status')}")
    print(f"  tags:                 {d.get('tags')}")
    if version_info.get("url"):
        print(f"  source (git):         {version_info.get('url')} @ {version_info.get('branch')}")
    print("---\n")


def main() -> None:
    api_key = os.environ.get("PREFECT_API_KEY")
    if not api_key:
        print(
            "Error: Set PREFECT_API_KEY (Prefect Cloud API key).",
            file=sys.stderr,
        )
        sys.exit(1)

    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(PREFECT_API_URL, headers=headers, timeout=60)

    if response.status_code != 200:
        print(f"Error: status {response.status_code}")
        print(response.text)
        sys.exit(1)

    deployment_info = response.json()
    _print_deployment_summary(deployment_info)
    print("Full JSON response:\n")
    print(json.dumps(deployment_info, indent=2))


if __name__ == "__main__":
    main()
