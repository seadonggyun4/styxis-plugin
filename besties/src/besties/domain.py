"""Host-independent, versioned public facts and presentation contracts.

Research labels, generation prompts and private review notes are not input fields.
All prose is reviewed input: reference binding is not semantic fact checking.
"""
from copy import deepcopy
from dataclasses import dataclass
from .model import fields, identifier, public_url, public_reference_url, require, text


@dataclass(frozen=True)
class ProductFacts:
    data: dict

    @classmethod
    def parse(cls, data):
        require(isinstance(data, dict), 'Facts object required')
        version = data.get('schema_version')
        require(type(version) is int and version in (1, 2), 'Unsupported facts schema')
        fields(data, ('schema_version', 'product', 'claims', 'evidence') + (('entity',) if version == 2 else ()))
        fields(data['product'], ('id', 'name', 'category', 'version'))
        identifier(data['product']['id'])
        for key in ('name', 'category', 'version'): text(data['product'][key])
        for key in ('claims', 'evidence'):
            require(isinstance(data[key], list) and 1 <= len(data[key]) <= 100, 'Invalid collection')
            ids = [identifier(row['id']) for row in data[key]]
            require(len(ids) == len(set(ids)), 'Duplicate identifier')
        evidence = {e['id'] for e in data['evidence']}
        for row in data['evidence']:
            fields(row, ('id', 'url', 'label', 'visibility'))
            (public_reference_url if version == 2 else public_url)(row['url']); text(row['label'])
            require(row['visibility'] == 'public', 'Public evidence required')
        for row in data['claims']:
            fields(row, ('id', 'statement', 'kind', 'evidence'))
            text(row['statement'])
            require(row['kind'] in ('identity', 'capability', 'limitation'), 'Invalid claim kind')
            require(isinstance(row['evidence'], list) and row['evidence'] and
                    all(e in evidence for e in row['evidence']), 'Unbound evidence')
        if version == 2:
            from .places import validate_entity
            validate_entity(data['entity'], evidence)
        return cls(deepcopy(data))

    @classmethod
    def from_project(cls, project):
        return cls.parse({'schema_version': 1, **{k: project.data[k] for k in ('product', 'claims', 'evidence')}})


@dataclass(frozen=True)
class PersonaDefinition:
    """Public editorial projection, independent of any personality taxonomy."""
    data: dict

    @classmethod
    def parse(cls, data):
        fields(data, ('schema_version', 'id', 'version', 'language', 'audience',
                      'title', 'description', 'heading', 'intro', 'sections'))
        require(type(data['schema_version']) is int and data['schema_version'] == 1, 'Unsupported presentation schema')
        identifier(data['id'])
        require(data['language'] in ('en', 'ko'), 'Unsupported editorial language')
        for key in ('version', 'audience', 'title', 'description', 'heading', 'intro'): text(data[key])
        require(10 <= len(data['title']) <= 100 and 40 <= len(data['description']) <= 300, 'Invalid metadata length')
        require(isinstance(data['sections'], list) and 1 <= len(data['sections']) <= 30, 'Invalid sections')
        ids = []
        for section in data['sections']:
            fields(section, ('id', 'heading', 'explanation', 'claim_ids'))
            ids.append(identifier(section['id']))
            text(section['heading']); text(section['explanation'])
            require(isinstance(section['claim_ids'], list) and section['claim_ids'], 'Claim bindings required')
            for claim in section['claim_ids']: identifier(claim)
        require(len(ids) == len(set(ids)), 'Duplicate section')
        return cls(deepcopy(data))


@dataclass(frozen=True)
class ContentPlan:
    data: dict
