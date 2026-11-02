"""Explicit UI/output-format locks, independent of editorial text and hosting."""
from html.parser import HTMLParser
from .model import require
from .resources import digest, encoded


class Structure(HTMLParser):
    def __init__(self):
        super().__init__(); self.events = []
    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        # Text and URLs may change; layout/style/accessibility hooks may not.
        selected = {k: v for k, v in attributes.items()
                    if k in ('class', 'id', 'style', 'role', 'type', 'name', 'rel', 'lang')
                    or k.startswith('aria-')}
        self.events.append(['open', tag, selected])
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs); self.handle_endtag(tag)
    def handle_endtag(self, tag):
        self.events.append(['close', tag])


def freeze_layout(files):
    """Call only when establishing or explicitly approving a new layout baseline."""
    html = {}
    for name, raw in files.items():
        if name.endswith('.html'):
            parser = Structure(); parser.feed(raw.decode())
            html[name] = digest(encoded(parser.events))
    require(bool(html), 'HTML pages required')
    return {'schema_version': 1, 'artifacts': sorted(files), 'html_structure': html,
            'stylesheets': {k: digest(v) for k, v in sorted(files.items()) if k.endswith('.css')}}


def verify_layout(files, approved):
    require(freeze_layout(files) == approved, 'Publication layout changed; explicit new baseline required')
    return {'passed': True, 'layout': 'unchanged'}
