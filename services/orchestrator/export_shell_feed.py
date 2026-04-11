"""Export latest orchestrator run artifacts into ui/shell/orchestrator-feed.json."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = REPO_ROOT / "data" / "demo" / "runs"
OUT_PATH = REPO_ROOT / "ui" / "shell" / "orchestrator-feed.json"


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

    OUT_PATH.write_text(json.dumps({"activity": activity, "memory": memory}, indent=2), encoding="utf-8")
    print(f"wrote {OUT_PATH.relative_to(REPO_ROOT)} from {len(latest)} run artifact(s)")
    return 0


def _fmt_ts(raw: object) -> str:
    if isinstance(raw, (float, int)):
        import datetime as _dt

        return _dt.datetime.fromtimestamp(raw, _dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    return "unknown time"


if __name__ == "__main__":
    raise SystemExit(main())
