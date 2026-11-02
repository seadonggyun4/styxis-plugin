"""Thin filesystem/network boundary for the independent presentation pipeline."""
import json
from types import SimpleNamespace
from .domain import ProductFacts, PersonaDefinition
from .planning import compose
from .rendering import render, plan_digest
from .resources import ResourceSite, encoded, verify_files_live
from .publishing import write_bundle, verify_files


def run(args, parser):
    if not args.persona: parser.error('--persona is required')
    raw = json.loads(args.manifest.read_text())
    if 'policy' in raw:
        from .model import Project
        facts = ProductFacts.from_project(Project.parse(raw))
    else:
        facts = ProductFacts.parse(raw)
    persona = PersonaDefinition.parse(json.loads(args.persona.read_text()))
    plan = compose(facts, persona)
    if args.command == 'plan-persona':
        if not args.output: parser.error('--output is required')
        write_bundle({'plan.json': encoded(plan.data)}, args.output)
        return {'plan_sha256': plan_digest(plan), 'review_required': True}
    if not args.site or not args.approved_plan_sha256:
        parser.error('--site and --approved-plan-sha256 are required')
    # Standalone facts do not require query/target configuration to build a site.
    site = ResourceSite.parse(json.loads(args.site.read_text()), SimpleNamespace(data={'targets': []}))
    from .model import require
    require(site.data['schema_version'] == 1, 'Presentation pipeline uses site schema 1; editorial data belongs to the plan')
    files = render(plan, site, args.approved_plan_sha256)
    if args.command == 'build-persona':
        if not args.output: parser.error('--output is required')
        write_bundle(files, args.output)
        return verify_files(files, args.output)
    if args.command == 'verify-persona':
        if not args.directory: parser.error('--directory is required')
        return verify_files(files, args.directory)
    if not args.live: parser.error('--live is required')
    result = verify_files_live(files, site.data['resource_url'])
    if args.output: write_bundle({'result.json': encoded(result)}, args.output)
    return result
