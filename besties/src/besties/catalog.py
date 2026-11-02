"""Private persona systems and public deployment bindings, without host SDKs.

Stable member numbers belong to a versioned domain definition, not an environment
variable or list position. Only explicit public projections may enter renderers.
"""
from dataclasses import dataclass
import re
from urllib.parse import urlsplit
from .model import fields, identifier, text, require, public_url


@dataclass(frozen=True, repr=False)
class PersonaMember:
    key: str
    number: int
    presentation_id: str


@dataclass(frozen=True, repr=False)
class PersonaSystem:
    framework: str
    version: str
    members: tuple[PersonaMember, ...]

    @classmethod
    def parse(cls, data):
        fields(data, ('framework', 'version', 'members'))
        text(data['framework']); text(data['version'])
        require(isinstance(data['members'], list) and 1 <= len(data['members']) <= 256, 'Invalid persona system size')
        members = []
        for item in data['members']:
            fields(item, ('key', 'number', 'presentation_id'))
            require(isinstance(item['key'], str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', item['key']), 'Invalid member key')
            require(type(item['number']) is int and item['number'] > 0, 'Positive member number required')
            identifier(item['presentation_id'])
            members.append(PersonaMember(**item))
        require(len({m.key for m in members}) == len(members), 'Duplicate member key')
        require(len({m.presentation_id for m in members}) == len(members), 'Duplicate presentation binding')
        require({m.number for m in members} == set(range(1, len(members) + 1)), 'Numbers must uniquely cover the declared members')
        return cls(data['framework'], data['version'], tuple(sorted(members, key=lambda m: m.number)))

    def check_successor(self, previous):
        """Appending members is supported; reassigning existing identities needs a migration."""
        require(self.framework == previous.framework, 'Framework identity changed')
        current = {m.key: m for m in self.members}
        require(all(current.get(m.key) == m for m in previous.members), 'Existing member identity changed; explicit migration required')
        require(self.members == previous.members or self.version != previous.version, 'Changed system requires a new version')


@dataclass(frozen=True)
class SiteIdentity:
    key: str
    role: str
    number: int | None
    presentation_id: str | None


@dataclass(frozen=True)
class NamingPolicy:
    product: str
    purpose: str

    @classmethod
    def parse(cls, data):
        fields(data, ('schema_version', 'product', 'purpose'))
        require(type(data['schema_version']) is int and data['schema_version'] == 1, 'Unsupported naming policy')
        return cls(identifier(data['product']), identifier(data['purpose']))

    def project_name(self, site):
        require(site.role in ('baseline', 'persona'), 'Unknown site role')
        if site.role == 'baseline':
            require(site.number is None, 'Baseline has no persona number')
            suffix = 'baseline'
        else:
            require(type(site.number) is int and site.number > 0, 'Persona number required')
            suffix = f'no-{site.number}'
        return identifier(f'{self.product}-{self.purpose}-{suffix}')


def origin(value):
    public_url(value)
    parsed = urlsplit(value)
    require(parsed.path in ('', '/') and parsed.port in (None, 443)
            and not any(c.isspace() for c in value), 'HTTPS origin required')
    return value.rstrip('/')


@dataclass(frozen=True)
class DeploymentBinding:
    site_key: str
    provider: str
    project: str
    url: str
    canonical_url: str

    def public_site(self, documentation_url, product_url):
        """Strict projection: never include framework/member keys or local paths."""
        return {'schema_version': 1, 'resource_url': self.url,
                'canonical_url': self.canonical_url, 'documentation_url': public_url(documentation_url),
                'product_url': public_url(product_url)}


@dataclass(frozen=True)
class DeploymentRegistry:
    providers: tuple[str, ...]
    canonical_provider: str
    bindings: tuple[DeploymentBinding, ...]

    @classmethod
    def parse(cls, data, sites, naming):
        registry = data
        fields(registry, ('providers', 'canonical_provider', 'bindings'))
        require(isinstance(registry['providers'], list) and bool(registry['providers']), 'Providers required')
        providers = tuple(identifier(p) for p in registry['providers'])
        require(len(set(providers)) == len(providers) and registry['canonical_provider'] in providers, 'Invalid provider set')
        require(isinstance(registry['bindings'], list), 'Deployment bindings required')
        expected = {(s.key, p) for s in sites for p in providers}
        selected = {}; urls = set(); projects = set()
        by_key = {s.key: s for s in sites}
        for row in registry['bindings']:
            fields(row, ('site_key', 'provider', 'project', 'url', 'canonical_url'))
            identifier(row['site_key']); identifier(row['provider']); identifier(row['project'])
            key = (row['site_key'], row['provider'])
            require(key in expected and key not in selected, 'Unknown or duplicate deployment binding')
            require(row['project'] == naming.project_name(by_key[row['site_key']]), 'Deployment project disagrees with naming policy')
            url, canonical = origin(row['url']), origin(row['canonical_url'])
            require(url not in urls and (row['provider'], row['project']) not in projects, 'Deployment address collision')
            urls.add(url); projects.add((row['provider'], row['project']))
            selected[key] = DeploymentBinding(row['site_key'], row['provider'], row['project'], url, canonical)
        require(set(selected) == expected, 'Incomplete deployment registry')
        for binding in selected.values():
            require(binding.canonical_url == selected[(binding.site_key, registry['canonical_provider'])].url,
                    'Canonical must identify the same presentation on its designated provider')
        return cls(providers, registry['canonical_provider'],
                   tuple(selected[(s.key, p)] for s in sites for p in providers))

@dataclass(frozen=True, repr=False)
class PublicationCatalog:
    system: PersonaSystem
    naming: NamingPolicy
    sites: tuple[SiteIdentity, ...]
    registry: DeploymentRegistry

    @classmethod
    def parse(cls, data):
        fields(data, ('schema_version', 'persona_system', 'naming', 'deployments'))
        require(type(data['schema_version']) is int and data['schema_version'] == 1, 'Unsupported catalog schema')
        system = PersonaSystem.parse(data['persona_system'])
        naming = NamingPolicy.parse(data['naming'])
        sites = (SiteIdentity('baseline', 'baseline', None, None),) + tuple(
            SiteIdentity(f'persona-{m.number}', 'persona', m.number, m.presentation_id) for m in system.members)
        return cls(system, naming, sites, DeploymentRegistry.parse(data['deployments'], sites, naming))

    @property
    def deployments(self):
        return self.registry.bindings

    @property
    def providers(self):
        return self.registry.providers

    @property
    def canonical_provider(self):
        return self.registry.canonical_provider

    def site(self, key):
        matches = [s for s in self.sites if s.key == key]
        require(len(matches) == 1, 'Unknown site identity')
        return matches[0]

    def binding(self, key, provider):
        matches = [b for b in self.deployments if b.site_key == key and b.provider == provider]
        require(len(matches) == 1, 'Unknown deployment binding')
        return matches[0]

    def check_presentation(self, key, presentation):
        site = self.site(key)
        require(site.role == 'persona' and presentation.data['id'] == site.presentation_id,
                'Presentation does not belong to this site identity')

    def check_targets(self, targets):
        """Validate private input rows before any build or external publishing call."""
        seen = set()
        for row in targets:
            binding = self.binding(row['site_key'], row['provider'])
            pair = (binding.site_key, binding.provider)
            require(pair not in seen and row['project'] == binding.project, 'Invalid or duplicate input target')
            seen.add(pair)
        require(seen == {(b.site_key, b.provider) for b in self.deployments}, 'Input targets do not cover the catalog')
