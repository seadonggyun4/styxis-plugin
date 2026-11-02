"""Official-CLI static publishers; no Git integration or credential handling."""
from dataclasses import dataclass
import json
import subprocess
from .model import identifier, require


def execute(command, directory):
    result = subprocess.run(command, cwd=directory, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)
    require(result.returncode == 0, 'Provider command did not complete successfully; reconcile before retry')
    return json.loads(result.stdout)


@dataclass(frozen=True)
class StaticPublisher:
    provider: str
    cli: tuple
    project: str
    team: str
    create_if_missing: bool = False
    runner: object = execute

    def deploy(self, directory):
        require(self.provider in ('vercel', 'netlify'), 'Unsupported provider')
        identifier(self.project); identifier(self.team)
        require(bool(self.cli) and all(isinstance(v, str) and v for v in self.cli), 'Explicit CLI required')
        require(not any(p.name in ('.git', '.env', '.env.local') for p in directory.rglob('*')), 'Source or environment data in static directory')
        if self.provider == 'vercel':
            args = ['deploy', str(directory), '--prod', '--yes', '--project', self.project,
                    '--scope', self.team, '--json']
            if self.create_if_missing: args += ['--create-if-missing']
        else:
            args = ['deploy', '--dir', str(directory), '--prod', '--no-build', '--json']
            args += (['--site-name', self.project, '--team', self.team] if self.create_if_missing
                     else ['--site', self.project])
        raw = self.runner([*self.cli, *args], directory)
        # Restrict receipts to identifiers; never persist raw provider responses.
        selected = {key: raw[key] for key in ('id', 'deploy_id', 'url', 'deploy_url', 'site_id')
                    if key in raw and isinstance(raw[key], str)}
        require(bool(selected), 'Missing deployment receipt; reconcile provider state')
        return json.dumps(selected, sort_keys=True)
