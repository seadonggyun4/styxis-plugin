"""Pure planning: same facts + reviewed presentation produce the same plan."""
from copy import deepcopy
from .domain import ContentPlan, ProductFacts, PersonaDefinition
from .model import require


def compose(facts: ProductFacts, persona: PersonaDefinition) -> ContentPlan:
    # Revalidate at the boundary: frozen dataclasses do not freeze nested mappings.
    facts = ProductFacts.parse(facts.data)
    persona = PersonaDefinition.parse(persona.data)
    expected = {c['id'] for c in facts.data['claims']}
    selected = [key for section in persona.data['sections'] for key in section['claim_ids']]
    require(len(selected) == len(set(selected)) and set(selected) == expected,
            'Every fact, including every limitation, must appear exactly once')
    return ContentPlan({'schema_version': 1, 'facts': deepcopy(facts.data),
                        'presentation': deepcopy(persona.data)})
