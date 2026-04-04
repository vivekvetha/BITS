# Prefect Cloud API: https://app.prefect.cloud/api/docs
#
# Usage:
#   export PREFECT_API_KEY="pnu_..."   # required — never commit real keys
#   python Prefect/api/flowAPI.py

import json
import os
import sys

import requests

ACCOUNT_ID = "37604d35-88fc-4011-9763-0d9cf1b6871f"
WORKSPACE_ID = "92d71a09-2bc6-4a9a-b524-98216df7b1e4"
FLOW_ID = "394e95a8-932c-4ed5-a23f-483fc40314d4"

PREFECT_API_URL = (
    f"https://api.prefect.cloud/api/accounts/{ACCOUNT_ID}"
    f"/workspaces/{WORKSPACE_ID}/flows/{FLOW_ID}"
)


def _print_flow_summary(f: dict) -> None:
    created_by = f.get("created_by") or {}
    print("\n--- Flow summary (for report) ---")
    print(f"  name:           {f.get('name')}")
    print(f"  id:             {f.get('id')}")
    print(f"  created:        {f.get('created')}")
    print(f"  updated:        {f.get('updated')}")
    print(f"  tags:           {f.get('tags')}")
    if created_by.get("display_value"):
        print(f"  created_by:     {created_by.get('display_value')}")
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

    flow_info = response.json()
    _print_flow_summary(flow_info)
    print("Full JSON response:\n")
    print(json.dumps(flow_info, indent=2))


if __name__ == "__main__":
    main()
