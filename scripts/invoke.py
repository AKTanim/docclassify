"""Call the Lambda handler on your computer, the way AWS would.

Usage: uv run python scripts/invoke.py events/quote.json
"""

import json
import sys
from pathlib import Path

from docclassify.handler import lambda_handler


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: uv run python scripts/invoke.py <event file>")
    # JSON event to dictionary
    event = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    response = lambda_handler(event, None)
    print(json.dumps(response, indent=2))  # back to JSON


if __name__ == "__main__":
    main()
