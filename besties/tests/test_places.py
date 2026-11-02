"""Synthetic inputs only; no customer or private study definitions."""
import json
import unittest
from copy import deepcopy
from test_presentations import facts, persona, site
from besties.domain import ProductFacts, PersonaDefinition
from besties.planning import compose
from besties.rendering import render, plan_digest
from besties.resources import encoded, digest
from besties.validation import validate_bundle
from besties.model import ContractError


def place_plan(language='ko'):
    f = facts().data
    f['schema_version'] = 2
    f['product']['name'] = '예시 식당'
    f['entity'] = {'type': 'Restaurant', 'address': {'streetAddress': '예시로 1', 'addressLocality': '예시시', 'addressRegion': '예시도', 'addressCountry': 'KR'}, 'telephone': '+82-2-000-0000', 'evidence': ['manual']}
    p = persona().data
    p.update(language=language, title='예시 식당 위치와 방문 안내', heading='방문 전에 확인하세요', description='공개 출처를 바탕으로 위치와 방문 전 확인 사항을 정리한 안내입니다. 현재 정보는 매장에 확인하세요.', intro='주소를 확인하고 방문을 준비하세요.')
    return compose(ProductFacts.parse(f), PersonaDefinition.parse(p))


class PlaceTests(unittest.TestCase):
    def test_korean_restaurant_shared_plan_contacts_and_no_software_assumption(self):
        p=place_plan(); files=render(p,site(),plan_digest(p)); html=files['index.html'].decode()
        self.assertIn('lang="ko"',html);self.assertIn('"@type": "Restaurant"',html)
        self.assertNotIn('SoftwareApplication',html);self.assertNotIn('Official documentation',html)
        self.assertNotIn('aggregateRating',html);self.assertIn('tel:+82-2-000-0000',html)
        self.assertTrue(validate_bundle(p,site(),files)['passed'])
        self.assertEqual(files,render(p,site(),plan_digest(p)))
        rebuilt=compose(ProductFacts.parse(json.loads(encoded(p.data['facts']))),PersonaDefinition.parse(json.loads(encoded(p.data['presentation']))))
        self.assertEqual(files,render(rebuilt,site(),plan_digest(rebuilt)))

    def test_english_place_localization(self):
        p=place_plan('en');files=render(p,site(),plan_digest(p))
        self.assertIn(b'Call the restaurant',files['index.html'])
        self.assertIn(b'lang="en"',files['index.html'])

    def test_entity_changes_invalidate_review(self):
        p=place_plan();review=plan_digest(p);p.data['facts']['entity']['telephone']='+82-2-000-1111'
        with self.assertRaises(ContractError):render(p,site(),review)

    def test_unknown_entity_fields_and_unbound_sources_fail(self):
        original=place_plan().data['facts']
        for key,value in [('type','SoftwareApplication'),('telephone','javascript:alert(1)'),('evidence',['unknown']),('openingHours','invented')]:
            f=deepcopy(original);f['entity'][key]=value
            with self.assertRaises(ContractError):ProductFacts.parse(f)

    def test_entity_markup_drift_fails_even_with_rehashed_artifact(self):
        p=place_plan();files=render(p,site(),plan_digest(p))
        files['index.html']=files['index.html'].replace(b'"@type": "Restaurant"',b'"@type": "SoftwareApplication"')
        receipt=json.loads(files['release.json']);receipt['files']['index.html']=digest(files['index.html']);files['release.json']=encoded(receipt)
        with self.assertRaises(ContractError):validate_bundle(p,site(),files)

    def test_legacy_template_and_generator_identity_retained(self):
        # Public synthetic v1 content must keep its original renderer and receipt.
        p=compose(facts(),persona());files=render(p,site(),plan_digest(p))
        self.assertEqual(json.loads(files['release.json'])['template_version'],'presentation-1')
        self.assertEqual(json.loads(files['release.json'])['generator_version'],'0.4.0')


class ReferenceTests(unittest.TestCase):
    def test_public_document_selectors_do_not_relax_origin_or_credentials(self):
        from besties.model import public_reference_url, public_url
        good='https://example.org/view?contentsid=DOC_123'
        self.assertEqual(public_reference_url(good),good)
        with self.assertRaises(ContractError):public_url(good)
        for bad in ('https://example.org/?token=secret','https://user:pass@example.org/','https://example.org/?id=a&id=b','https://example.org/#private'):
            with self.assertRaises(ContractError):public_reference_url(bad)
