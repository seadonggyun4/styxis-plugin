import copy
import json
import unittest
import contextlib
import io
import tempfile
from pathlib import Path
from besties.catalog import PublicationCatalog, PersonaSystem
from besties.domain import PersonaDefinition
from besties.model import ContractError
from test_presentations import persona, facts
from besties.planning import compose
from besties.rendering import render, plan_digest
from besties.resources import ResourceSite
from types import SimpleNamespace


def definition(count=2):
    members = [{'key': f'Type{n}', 'number': n, 'presentation_id': f'view-{n}'} for n in range(1, count + 1)]
    bindings = []
    for number in [None, *range(1, count + 1)]:
        key = 'baseline' if number is None else f'persona-{number}'
        name = 'sample-resource-' + ('baseline' if number is None else f'no-{number}')
        for provider in ('host-a', 'host-b'):
            bindings.append(dict(site_key=key, provider=provider, project=name,
                url=f'https://{name}.{provider}.example.org',
                canonical_url=f'https://{name}.host-a.example.org'))
    return dict(schema_version=1, persona_system=dict(framework='Private editorial system', version='1', members=members),
                naming=dict(schema_version=1, product='sample', purpose='resource'),
                deployments=dict(providers=['host-a', 'host-b'], canonical_provider='host-a', bindings=bindings))


class CatalogTests(unittest.TestCase):
    def test_cli_validates_without_disclosing_private_system(self):
        from besties.cli import main
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'catalog.json'; path.write_text(json.dumps(definition()))
            output=io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(['validate-catalog',str(path)]),0)
            result=json.loads(output.getvalue())
            self.assertEqual(result['bindings'],6)
            self.assertNotIn('Private editorial system',output.getvalue())
            self.assertNotIn('Type1',output.getvalue())

    def test_size_and_order_come_from_domain_not_environment(self):
        for count in (2, 5, 17):
            raw = definition(count); raw['persona_system']['members'].reverse()
            c = PublicationCatalog.parse(raw)
            self.assertEqual(len(c.sites), count + 1)
            self.assertEqual(c.sites[0].role, 'baseline')
            self.assertIsNone(c.sites[0].number)
            self.assertEqual(c.sites[-1].number, count)
            self.assertEqual(len(c.deployments), 2 * (count + 1))

    def test_member_identity_changes_require_migration(self):
        old = PersonaSystem.parse(definition()['persona_system'])
        raw = definition(3)['persona_system']; raw['version'] = '2'
        PersonaSystem.parse(raw).check_successor(old)
        raw['version'] = '1'
        with self.assertRaises(ContractError): PersonaSystem.parse(raw).check_successor(old)
        raw = definition()['persona_system']
        raw['members'][0]['number'], raw['members'][1]['number'] = 2, 1
        with self.assertRaises(ContractError): PersonaSystem.parse(raw).check_successor(old)

    def test_duplicate_missing_and_boolean_member_numbers_rejected(self):
        for field, value in [('number', 2), ('number', 3), ('number', True), ('key', 'Type2'), ('presentation_id', 'view-2')]:
            raw = definition(); raw['persona_system']['members'][0][field] = value
            with self.assertRaises(ContractError): PublicationCatalog.parse(raw)

    def test_missing_duplicate_and_unbound_registry_rows_rejected(self):
        for transform in (lambda rows: rows.pop(), lambda rows: rows.append(copy.deepcopy(rows[0])),
                          lambda rows: rows[0].update(site_key='persona-99'),
                          lambda rows: rows[0].update(project='arbitrary-name')):
            raw=definition(); transform(raw['deployments']['bindings'])
            with self.assertRaises(ContractError): PublicationCatalog.parse(raw)

    def test_cross_persona_canonical_and_address_collision_rejected(self):
        raw=definition(); rows=raw['deployments']['bindings']
        rows[3]['canonical_url']=rows[0]['url']
        with self.assertRaises(ContractError): PublicationCatalog.parse(raw)
        raw=definition(); raw['deployments']['bindings'][1]['url']=raw['deployments']['bindings'][0]['url']
        with self.assertRaises(ContractError): PublicationCatalog.parse(raw)

    def test_custom_domains_are_recorded_not_inferred_from_project_name(self):
        raw=definition(); raw['deployments']['bindings'][3]['url']='https://custom.example.net'
        c=PublicationCatalog.parse(raw)
        self.assertEqual(c.binding('persona-1','host-b').url,'https://custom.example.net')

    def test_public_projection_and_render_never_include_private_taxonomy(self):
        c=PublicationCatalog.parse(definition()); raw=persona().data; raw['id']='view-1'
        p=PersonaDefinition.parse(raw); c.check_presentation('persona-1',p)
        site=ResourceSite.parse(c.binding('persona-1','host-a').public_site('https://docs.example.org','https://product.example.org'),SimpleNamespace(data={'targets':[]}))
        plan=compose(facts(),p); files=render(plan,site,plan_digest(plan))
        published=b'\n'.join(files.values()).decode()
        self.assertNotIn('Private editorial system',published)
        self.assertNotIn('Type1',published)
        self.assertNotIn('Private editorial system',repr(c))
        with self.assertRaises(ContractError): c.check_presentation('persona-2',p)
        with self.assertRaises(ContractError): c.check_presentation('baseline',p)

    def test_operator_input_inventory_must_cover_exact_catalog(self):
        c=PublicationCatalog.parse(definition())
        rows=[dict(site_key=b.site_key,provider=b.provider,project=b.project) for b in c.deployments]
        c.check_targets(rows)
        with self.assertRaises(ContractError): c.check_targets(rows[:-1])
        with self.assertRaises(ContractError): c.check_targets(rows+[rows[0]])

    def test_generic_product_and_unknown_framework_need_no_code_changes(self):
        raw=definition(); raw['persona_system']['framework']='Another system'
        raw['naming']['product']='another-product'
        for row in raw['deployments']['bindings']: row['project']=row['project'].replace('sample-','another-product-')
        c=PublicationCatalog.parse(raw)
        self.assertEqual(c.naming.project_name(c.site('persona-1')),'another-product-resource-no-1')
