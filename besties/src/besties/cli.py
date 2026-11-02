"""CLI boundary; outputs require a new directory and never modify site files."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from .model import Project, ContractError
from .planner import plan, render
from .audit import audit
from .adapters import HTTPReader
from .evaluation import evaluate


def main(argv=None):
    parser = argparse.ArgumentParser(prog="besties")
    parser.add_argument("command", choices=("validate", "plan", "audit", "evaluate"))
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--live", action="store_true", help="Allow GET requests to configured target URLs")
    parser.add_argument("--observations", type=Path)
    args = parser.parse_args(argv)
    try:
        project = Project.parse(json.loads(args.manifest.read_text(encoding="utf-8")))
        if args.command == "validate":
            print(json.dumps({"valid": True, "product_id": project.data["product"]["id"]}))
            return 0
        if not args.output:
            parser.error("--output is required")
        if args.command == "audit" and not args.live:
            parser.error("audit requires --live; offline audits use the Reader API")
        if args.command == "evaluate" and not args.observations:
            parser.error("evaluate requires --observations")
        imported = evaluate(project, json.loads(args.observations.read_text(encoding="utf-8"))) if args.command == "evaluate" else None
        # Fail before external calls if output already exists.
        args.output.mkdir(parents=True, exist_ok=False)
        if args.command == "plan":
            result = plan(project)
            (args.output / "draft.html").write_text(render(project), encoding="utf-8")
        elif args.command == "evaluate":
            result = imported
        else:
            result = audit(project, HTTPReader(t["url"] for t in project.data["targets"]))
            result["observed_at"] = datetime.now(timezone.utc).isoformat()
        (args.output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"command": args.command, "completed": True}))
        return 0 if args.command != "audit" or result["passed"] else 1
    except (ContractError, ValueError, OSError, TypeError, KeyError):
        parser.exit(2, "Invalid input or unavailable output; inspect the local manifest and output directory.\n")


if __name__ == "__main__":
    raise SystemExit(main())
