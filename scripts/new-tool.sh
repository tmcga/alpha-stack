#!/usr/bin/env bash
# Scaffold a new Alpha Stack Python tool with the standard pattern.
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <tool-name>"
  echo "Example: $0 sharpe_ratio"
  exit 1
fi

NAME="$1"
FILE="tools/${NAME}.py"

if [ -f "$FILE" ]; then
  echo "Error: $FILE already exists"
  exit 1
fi

cat > "$FILE" << 'TEMPLATE'
#!/usr/bin/env python3
"""TOOL_DESC

Usage:
    python TOOL_NAME.py --param1 VALUE --param2 VALUE
"""

import argparse


def FUNC_NAME(
    param1: float,
    param2: float,
) -> dict:
    """One-line description of the calculation.

    Args:
        param1: Description.
        param2: Description.

    Returns:
        Dict with results.
    """
    # TODO: Implement calculation
    result = param1 + param2

    return {
        "result": result,
    }


def main():
    parser = argparse.ArgumentParser(description="TOOL_DESC")
    parser.add_argument("--param1", type=float, required=True, help="Description")
    parser.add_argument("--param2", type=float, required=True, help="Description")
    args = parser.parse_args()

    r = FUNC_NAME(args.param1, args.param2)

    print(f"\n{'=' * 50}")
    print("  TOOL_DESC")
    print(f"{'=' * 50}")
    print(f"  Result: {r['result']:>12.4f}")
    print(f"{'=' * 50}\n")


if __name__ == "__main__":
    main()
TEMPLATE

# Replace placeholders
FUNC=$(echo "$NAME" | tr '-' '_')
DESC=$(echo "$NAME" | tr '_-' '  ')
sed -i '' "s/TOOL_NAME/$NAME/g" "$FILE"
sed -i '' "s/FUNC_NAME/$FUNC/g" "$FILE"
sed -i '' "s/TOOL_DESC/$DESC/g" "$FILE"

echo "Created: $FILE"
echo ""
echo "Next steps:"
echo "  1. Edit $FILE — implement the calculation"
echo "  2. Keep it under 200 lines, stdlib-only"
echo "  3. Add tests to tests/test_tools.py"
echo "  4. Register in mcp_server.py (optional)"
echo "  5. Open a PR"
