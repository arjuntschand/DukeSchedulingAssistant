from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv


def main() -> None:
    # Load .env from the backend directory explicitly, regardless of CWD
    backend_root = Path(__file__).resolve().parent.parent
    env_path = backend_root / ".env"
    load_dotenv(dotenv_path=env_path, override=False)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY is not set in the environment or .env file.")
        sys.exit(1)

    url = "https://openrouter.ai/api/v1/credits"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, headers=headers)
    except Exception as exc:  # pragma: no cover
        print(f"Error calling OpenRouter credits endpoint: {exc}")
        sys.exit(1)

    print(f"Status: {resp.status_code}")
    try:
        data = resp.json()
    except Exception:
        print("Non-JSON response body:")
        print(resp.text)
        sys.exit(1)

    # Pretty-print key fields if present
    total_credits = data.get("total_credits") or data.get("credits")
    total_usage = data.get("total_usage") or data.get("usage")

    print("OpenRouter credits:")
    print(f"  total_credits: {total_credits}")
    print(f"  total_usage:   {total_usage}")
    print("\nRaw JSON:")
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
