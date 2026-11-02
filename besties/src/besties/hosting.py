"""Official-CLI static publishers; no Git integration or credential handling."""
from dataclasses import dataclass
import json
import subprocess
from tempfile import TemporaryDirectory
from .model import identifier, require


def execute(command, directory, environment=None):
    # Provider CLIs write local state. Keep that state out of immutable artifacts
    # so a later rollback can verify and reuse the exact original bundle.
    with TemporaryDirectory(prefix='besties-provider-') as control:
        result = subprocess.run(command, cwd=control, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240,
                                env=environment)
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
        require(not any(p.name == '.git' or p.name == '.env' or p.name.startswith('.env.')
                        or p.name.startswith('env-') for p in directory.rglob('*')), 'Source or environment data in static directory')
        if self.provider == 'vercel':
            args = ['deploy', str(directory), '--prod', '--yes', '--project', self.project,
                    '--scope', self.team, '--json']
            if self.create_if_missing: args += ['--create-if-missing']
        else:
            args = ['deploy', '--dir', str(directory), '--prod', '--no-build', '--json']
            args += (['--site-name', self.project, '--team', self.team] if self.create_if_missing
                     else ['--site', self.project])
        if self.runner is execute:
            from .environment import process_environment
            raw = execute([*self.cli, *args], directory, environment=process_environment(self.provider))
        else:
            raw = self.runner([*self.cli, *args], directory)
        if self.provider == 'vercel':
            # Agent-mode CLIs wrap the response; regular CLI JSON may be flat.
            if 'deployment' in raw:
                require(raw.get('status') in ('ok', 'success') and isinstance(raw['deployment'], dict),
                        'Unexpected Vercel receipt; reconcile provider state')
                raw = raw['deployment']
            require(raw.get('readyState', 'READY') == 'READY', 'Vercel deployment not ready')
        # Restrict receipts to identifiers; never persist raw provider responses.
        selected = {key: raw[key] for key in ('id', 'deploy_id', 'url', 'deploy_url', 'site_id')
                    if key in raw and isinstance(raw[key], str)}
        require(bool(selected), 'Missing deployment receipt; reconcile provider state')
        return json.dumps(selected, sort_keys=True)
