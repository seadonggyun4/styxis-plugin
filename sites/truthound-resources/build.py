"""Build only the dedicated public resource artifact directory."""
from pathlib import Path
import json
import sys
import os

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'besties/src'))
from besties.model import Project
from besties.resources import ResourceSite, build, verify_directory

HERE = Path(__file__).resolve().parent
project = Project.parse(json.loads((ROOT / 'besties/examples/truthound/resource-project.json').read_text()))
provider = os.environ.get('BESTIES_HOST', 'netlify')
if provider not in ('netlify', 'vercel'):
    raise ValueError('Unsupported hosting adapter')
site = ResourceSite.parse(json.loads((ROOT / f'besties/examples/truthound/resource-site-{provider}.json').read_text()), project)
# Fail closed on stale output; clean checkouts provide an empty build location.
output = HERE / 'dist'
build(project, site, output)
print(json.dumps(verify_directory(project, site, output)))
