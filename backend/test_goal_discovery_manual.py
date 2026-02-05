#!/usr/bin/env python3
"""
Manual testing script for goal discovery endpoint.

Usage:
    python test_goal_discovery_manual.py <file_path> [--model MODEL]

Examples:
    python test_goal_discovery_manual.py ./data/sales.csv
    python test_goal_discovery_manual.py ./documents/business_plan.txt --model gpt-4.1-mini
    python test_goal_discovery_manual.py ./file1.txt ./file2.csv  # Multiple files

Requires:
    - Backend server running locally on port 8000
    - Valid authentication (will prompt for auth token)
    - API keys configured in backend
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)


# Configuration
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_MODEL = "gpt-5.2"


def read_file(file_path: str) -> dict:
    """Read file and return FileData dict."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_text(encoding="utf-8", errors="replace")

    # Determine file type
    suffix = path.suffix.lower()
    type_map = {
        ".csv": "text/csv",
        ".txt": "text/plain",
        ".json": "application/json",
        ".md": "text/markdown",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".pdf": "application/pdf",
    }
    file_type = type_map.get(suffix, "text/plain")

    return {
        "name": path.name,
        "content": content,
        "type": file_type,
        "size": len(content)
    }


def format_goal(goal: dict, index: int) -> str:
    """Format a single goal for display."""
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"GOAL {index + 1}: {goal.get('type', 'UNKNOWN')}")
    lines.append(f"{'='*60}")

    # Identity
    identity = goal.get("identity", "No identity")
    lines.append(f"\n📌 IDENTITY:")
    lines.append(f"   {identity}")
    word_count = len(identity.split())
    lines.append(f"   ({word_count} words)")

    # First Move
    first_move = goal.get("firstMove", "No first move")
    lines.append(f"\n🎯 FIRST MOVE:")
    lines.append(f"   {first_move}")
    word_count = len(first_move.split())
    lines.append(f"   ({word_count} words)")

    # Confidence
    confidence = goal.get("confidence", 0)
    bar_length = int(confidence * 20)
    bar = "█" * bar_length + "░" * (20 - bar_length)
    lines.append(f"\n📊 CONFIDENCE: [{bar}] {confidence:.1%}")

    # Source files
    source_files = goal.get("sourceFiles", [])
    lines.append(f"\n📁 SOURCE FILES: {', '.join(source_files)}")

    # Classification reason
    reason = goal.get("classification_reason", "No reason")
    lines.append(f"\n💡 CLASSIFICATION REASON:")
    lines.append(f"   {reason}")

    # Supporting signals (summary)
    signals = goal.get("supporting_signals", [])
    if signals:
        lines.append(f"\n📋 SUPPORTING SIGNALS ({len(signals)}):")
        for i, sig in enumerate(signals[:3]):  # Show first 3
            desc = sig.get("description", "")[:80]
            category = sig.get("category", "unknown")
            lines.append(f"   {i+1}. [{category}] {desc}...")
        if len(signals) > 3:
            lines.append(f"   ... and {len(signals) - 3} more")

    # Consciousness context (if present)
    ctx = goal.get("consciousness_context")
    if ctx:
        lines.append(f"\n🧠 CONSCIOUSNESS CONTEXT:")
        if "s_level" in ctx:
            lines.append(f"   S-Level: {ctx['s_level']}")
        if "drive_profile" in ctx:
            lines.append(f"   Drive: {ctx['drive_profile'].get('dominant', 'unknown')}")
        if "bottleneck_data" in ctx:
            bn = ctx["bottleneck_data"]
            lines.append(f"   Bottleneck: {bn.get('primary', 'none')} ({bn.get('value', 0):.2f})")

    return "\n".join(lines)


def format_usage(usage: dict) -> str:
    """Format token usage for display."""
    lines = []
    lines.append("\n" + "="*60)
    lines.append("TOKEN USAGE")
    lines.append("="*60)

    lines.append(f"\nCall 1 (Signal Extraction):")
    lines.append(f"   Input:  {usage.get('call1_input_tokens', 0):,} tokens")
    lines.append(f"   Output: {usage.get('call1_output_tokens', 0):,} tokens")

    lines.append(f"\nCall 2 (Articulation):")
    lines.append(f"   Input:  {usage.get('call2_input_tokens', 0):,} tokens")
    lines.append(f"   Output: {usage.get('call2_output_tokens', 0):,} tokens")

    lines.append(f"\nTOTAL:")
    lines.append(f"   Input:  {usage.get('total_input_tokens', 0):,} tokens")
    lines.append(f"   Output: {usage.get('total_output_tokens', 0):,} tokens")

    if usage.get("cache_read_tokens"):
        lines.append(f"\nCache Efficiency:")
        lines.append(f"   Read:  {usage.get('cache_read_tokens', 0):,} tokens")
        lines.append(f"   Write: {usage.get('cache_write_tokens', 0):,} tokens")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Manual testing script for goal discovery endpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python test_goal_discovery_manual.py ./data/sales.csv
    python test_goal_discovery_manual.py ./plan.txt --model gpt-4.1-mini
    python test_goal_discovery_manual.py file1.txt file2.csv --base-url http://api.example.com
        """
    )
    parser.add_argument("files", nargs="+", help="Path(s) to file(s) to analyze")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"Base URL (default: {DEFAULT_BASE_URL})")
    parser.add_argument("--token", help="Auth token (or set AUTH_TOKEN env var)")
    parser.add_argument("--raw", action="store_true", help="Print raw JSON response")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Get auth token
    auth_token = args.token or os.getenv("AUTH_TOKEN")
    if not auth_token:
        print("Warning: No auth token provided. Set --token or AUTH_TOKEN env var.")
        print("Attempting request without authentication...")

    # Read files
    print(f"\n📂 Reading {len(args.files)} file(s)...")
    file_data = []
    for file_path in args.files:
        try:
            data = read_file(file_path)
            file_data.append(data)
            print(f"   ✓ {data['name']} ({data['size']:,} bytes)")
        except FileNotFoundError as e:
            print(f"   ✗ {e}")
            sys.exit(1)

    # Build request
    request_body = {
        "files": file_data,
        "model": args.model,
        "existing_goals": None
    }

    # Make request
    endpoint = f"{args.base_url}/api/goals/discover-from-files"
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    print(f"\n🚀 Calling {endpoint}")
    print(f"   Model: {args.model}")
    print(f"   Files: {len(file_data)}")

    start_time = time.time()

    try:
        with httpx.Client(timeout=180.0) as client:
            response = client.post(endpoint, json=request_body, headers=headers)

        elapsed = time.time() - start_time

        if response.status_code != 200:
            print(f"\n❌ Error: HTTP {response.status_code}")
            print(f"   {response.text[:500]}")
            sys.exit(1)

        result = response.json()

    except httpx.TimeoutException:
        print(f"\n❌ Request timed out after 180 seconds")
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"\n❌ Request error: {e}")
        sys.exit(1)

    # Display results
    if args.raw:
        print("\n" + json.dumps(result, indent=2))
        return

    print(f"\n✅ Success! ({elapsed:.1f}s)")
    print(f"   Generated at: {result.get('generatedAt', 'unknown')}")
    print(f"   Source files: {result.get('sourceFileCount', 0)}")

    # Display goals
    goals = result.get("goals", [])
    print(f"\n🎯 DISCOVERED {len(goals)} GOALS")

    for i, goal in enumerate(goals):
        print(format_goal(goal, i))

    # Display usage
    usage = result.get("usage", {})
    print(format_usage(usage))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    goal_types = {}
    for goal in goals:
        t = goal.get("type", "UNKNOWN")
        goal_types[t] = goal_types.get(t, 0) + 1

    print(f"\nGoal types:")
    for goal_type, count in sorted(goal_types.items()):
        print(f"   {goal_type}: {count}")

    avg_confidence = sum(g.get("confidence", 0) for g in goals) / len(goals) if goals else 0
    print(f"\nAverage confidence: {avg_confidence:.1%}")
    print(f"Total time: {elapsed:.1f}s")
    print(f"Total tokens: {usage.get('total_input_tokens', 0) + usage.get('total_output_tokens', 0):,}")


if __name__ == "__main__":
    main()
