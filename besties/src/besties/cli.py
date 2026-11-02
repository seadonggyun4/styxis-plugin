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
from .resources import ResourceSite, build, verify_directory, verify_live


def main(argv=None):
    parser = argparse.ArgumentParser(prog="besties")
    parser.add_argument("command", choices=("validate", "plan", "audit", "evaluate", "build-resources", "verify-resources", "verify-resource-live", "plan-persona", "build-persona", "verify-persona", "verify-persona-live", "validate-environment", "validate-catalog"))
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--live", action="store_true", help="Allow GET requests to configured target URLs")
    parser.add_argument("--observations", type=Path)
    parser.add_argument("--site", type=Path, help="Separate resource-host configuration")
    parser.add_argument("--directory", type=Path, help="Existing resource bundle to verify")
    parser.add_argument("--persona", type=Path, help="Public presentation definition; research settings stay external")
    parser.add_argument("--approved-plan-sha256", help="Digest of the exact editorial plan reviewed for publication")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate-catalog":
            from .catalog import PublicationCatalog
            catalog = PublicationCatalog.parse(json.loads(args.manifest.read_text(encoding="utf-8")))
            print(json.dumps({"valid": True, "personas": len(catalog.system.members),
                              "sites": len(catalog.sites), "bindings": len(catalog.deployments),
                              "private_definition_redacted": True}))
            return 0
        if args.command == "validate-environment":
            from .environment import OperatorEnvironment
            print(json.dumps(OperatorEnvironment.load(args.manifest).summary()))
            return 0
        if args.command in ("plan-persona", "build-persona", "verify-persona", "verify-persona-live"):
            from .persona_cli import run
            result = run(args, parser)
            print(json.dumps(result, ensure_ascii=False))
            return 0 if result.get('passed', True) else 1
        project = Project.parse(json.loads(args.manifest.read_text(encoding="utf-8")))
        if args.command in ("build-resources", "verify-resources", "verify-resource-live"):
            if not args.site:
                parser.error("--site is required")
            site = ResourceSite.parse(json.loads(args.site.read_text(encoding="utf-8")), project)
            if args.command == "build-resources":
                if not args.output:
                    parser.error("--output is required")
                result = build(project, site, args.output)
            elif args.command == "verify-resources":
                if not args.directory:
                    parser.error("--directory is required")
                result = verify_directory(project, site, args.directory)
            else:
                if not args.live:
                    parser.error("verify-resource-live requires --live")
                if args.output:
                    args.output.mkdir(parents=True, exist_ok=False)
                result = verify_live(project, site)
                if args.output:
                    (args.output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(result, ensure_ascii=False))
            return 0 if result['passed'] else 1
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
