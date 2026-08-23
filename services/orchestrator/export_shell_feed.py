"""Export recent run artifacts for the optional static shell preview."""

from __future__ import annotations

import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = Path(os.environ.get("REFOCUS_DEMO_DATA_DIR", REPO_ROOT / "data" / "demo")) / "runs"
OUT_PATH = Path(
    os.environ.get("REFOCUS_DEMO_FEED_PATH", REPO_ROOT / "ui" / "shell" / "orchestrator-feed.json")
)


def main() -> int:
    runs = sorted(RUNS_DIR.glob("run-*.json"))
    latest = runs[-10:]
    activity = []
    memory = []
    for path in reversed(latest):
        payload = json.loads(path.read_text(encoding="utf-8"))
        result = payload.get("result", {})
        summary = result.get("planner_summary", {}).get("summary_text", result.get("message", "No message"))
        activity.append(
            {
                "title": f"{result.get('status', 'unknown').upper()} · {result.get('planner_decision', {}).get('worker_name', 'n/a')}",
                "detail": summary,
                "timestamp": _fmt_ts(payload.get("created_at")),
            }
        )
        if result.get("memory_recall"):
            memory.append(
                {
                    "label": f"Task {result.get('status', 'unknown')}",
                    "value": json.dumps(result["memory_recall"], ensure_ascii=False)[:220],
                }
            )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"activity": activity, "memory": memory}, indent=2), encoding="utf-8")
    try:
        display_path = OUT_PATH.relative_to(REPO_ROOT)
    except ValueError:
        display_path = OUT_PATH
    print(f"wrote {display_path} from {len(latest)} run artifact(s)")
    return 0


def _fmt_ts(raw: object) -> str:
    if isinstance(raw, (float, int)):
        import datetime as _dt

        return _dt.datetime.fromtimestamp(raw, _dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    return "unknown time"


if __name__ == "__main__":
    raise SystemExit(main())
